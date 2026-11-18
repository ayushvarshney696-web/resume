"""Domain exceptions for AI Resume Reviewer."""

class ResumeAppException(Exception):
    """Base exception for all application errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class FileTooLargeException(ResumeAppException):
    """Raised when an uploaded file exceeds the maximum size limit."""
    def __init__(self, message: str = "File size exceeds allowed limit."):
        super().__init__(message, status_code=413)

class UnsupportedFormatException(ResumeAppException):
    """Raised when an uploaded file has an unsupported extension or MIME type."""
    def __init__(self, message: str = "Unsupported file format."):
        super().__init__(message, status_code=400)

class TextTooShortException(ResumeAppException):
    """Raised when provided resume text is too short to analyze meaningfully."""
    def __init__(self, message: str = "Resume text is too short (minimum 30 characters required)."):
        super().__init__(message, status_code=400)

class CorruptedFileException(ResumeAppException):
    """Raised when a file archive or PDF cannot be parsed or is corrupted."""
    def __init__(self, message: str = "Could not parse or read document."):
        super().__init__(message, status_code=422)
