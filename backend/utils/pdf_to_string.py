from io import BytesIO
from pypdf import PdfReader

def pdf_to_string(pdf_bytes: bytes):
    print(">>> Converting PDF to text...")

    reader = PdfReader(BytesIO(pdf_bytes))
    text = []

    for page in reader.pages:
        text.append(page.extract_text() or "")

    return "\n".join(text)
