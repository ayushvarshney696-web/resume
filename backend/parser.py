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

MAX_PDF_PAGES = 30
MAX_XML_BYTES = 10 * 1024 * 1024  # 10 MB decompression limit

WHITESPACE_REGEX = re.compile(r"[ \t]+")
NEWLINE_REGEX = re.compile(r"\n{3,}")
CRLF_REGEX = re.compile(r"\r\n|\r")

def sanitize_text(text: str) -> str:
    """Normalize and sanitize text extracted from documents."""
    text = CRLF_REGEX.sub("\n", text)
    text = WHITESPACE_REGEX.sub(" ", text)
    text = NEWLINE_REGEX.sub("\n\n", text)
    return text.strip()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf or PyPDF2 with page limit protection."""
    if not PDF_READER:
        raise RuntimeError("Neither pypdf nor PyPDF2 is installed.")
    
    text_parts = []
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    page_count = min(len(reader.pages), MAX_PDF_PAGES)
    
    for page_idx in range(page_count):
        try:
            page = reader.pages[page_idx]
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_parts.append(page_text)
        except Exception:
            continue
            
    return sanitize_text("\n".join(text_parts))

def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using standard library zipfile with XML size guard."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as docx:
            # Check for zip bomb / excessively large XML
            doc_info = docx.getinfo("word/document.xml")
            if doc_info.file_size > MAX_XML_BYTES:
                raise ValueError("DOCX contents exceed safe decompression limit.")
                
            xml_content = docx.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            
            w_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            paragraphs = []
            
            for p in tree.iter(f"{w_ns}p"):
                texts = [node.text for node in p.iter(f"{w_ns}t") if node.text]
                if texts:
                    paragraphs.append("".join(texts))
                    
            return sanitize_text("\n".join(paragraphs))
    except zipfile.BadZipFile:
        raise ValueError("Invalid DOCX format or corrupted archive.")
    except Exception as e:
        raise ValueError(f"Could not parse DOCX file: {str(e)}")

def extract_text_from_txt(file_bytes: bytes) -> str:
    """Decode raw text bytes across multiple common encodings."""
    for encoding in ("utf-8", "utf-16", "latin-1", "cp1252"):
        try:
            return sanitize_text(file_bytes.decode(encoding))
        except UnicodeDecodeError:
            continue
    return sanitize_text(file_bytes.decode("utf-8", errors="ignore"))

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}

def extract_resume_text(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Safely extract text based on verified file extension.
    Returns (cleaned_text, detected_type)
    """
    fname_clean = filename.strip().lower()
    ext = "." + fname_clean.split(".")[-1] if "." in fname_clean else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    if ext == ".pdf":
        text = extract_text_from_pdf(file_bytes)
        file_type = "PDF Document"
    elif ext == ".docx":
        text = extract_text_from_docx(file_bytes)
        file_type = "Word Document (DOCX)"
    elif ext == ".doc":
        try:
            text = extract_text_from_docx(file_bytes)
            file_type = "Word Document"
        except Exception:
            text = extract_text_from_txt(file_bytes)
            file_type = "Word Document (Text Stream)"
    elif ext in (".txt", ".md"):
        text = extract_text_from_txt(file_bytes)
        file_type = "Plain Text"
    else:
        text = extract_text_from_txt(file_bytes)
        file_type = "Text Document"

    return sanitize_text(text), file_type
