import io
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Tuple

try:
    import pypdf
    PDF_READER = "pypdf"
except ImportError:
    try:
        import PyPDF2 as pypdf
        PDF_READER = "PyPDF2"
    except ImportError:
        PDF_READER = None

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf or PyPDF2."""
    if not PDF_READER:
        raise RuntimeError("Neither pypdf nor PyPDF2 is installed.")
    
    text_parts = []
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    for page_idx, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if page_text.strip():
            text_parts.append(page_text)
            
    return "\n".join(text_parts).strip()

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using standard library zipfile and XML parser."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx:
            xml_content = docx.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            
            # W namespace
            w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = []
            
            for p in tree.iter(f"{w_ns}p"):
                texts = [node.text for node in p.iter(f"{w_ns}t") if node.text]
                if texts:
                    paragraphs.append("".join(texts))
                    
            return "\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Could not parse DOCX file: {str(e)}")

def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode raw text bytes with multiple encodings."""
    for encoding in ("utf-8", "utf-16", "latin-1", "cp1252"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="ignore").strip()

def extract_resume_text(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Extract text based on file extension.
    Returns (cleaned_text, detected_type)
    """
    fname_lower = filename.lower()
    
    if fname_lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
        file_type = "PDF"
    elif fname_lower.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
        file_type = "DOCX"
    elif fname_lower.endswith(".doc"):
        # For legacy .doc binary files, try best-effort text extraction
        try:
            text = extract_text_from_docx(file_bytes)
            file_type = "DOC"
        except Exception:
            text = extract_text_from_txt(file_bytes)
            file_type = "DOC (Text Extracted)"
    elif fname_lower.endswith(".txt") or fname_lower.endswith(".md"):
        text = extract_text_from_txt(file_bytes)
        file_type = "TXT"
    else:
        # Fallback to UTF-8 text attempt
        text = extract_text_from_txt(file_bytes)
        file_type = "Generic Text"

    # Sanitize and normalize text
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip(), file_type
