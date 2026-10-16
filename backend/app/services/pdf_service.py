import io

from pypdf import PdfReader


def extract_text(data: bytes) -> str:
    """PDF bytes -> plain text."""
    reader = PdfReader(io.BytesIO(data))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text
