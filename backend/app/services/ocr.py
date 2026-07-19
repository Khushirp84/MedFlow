"""
Text extraction service.

Strategy:
1. If the file is a PDF, try PyMuPDF first (fast, works for text-native PDFs).
2. If a page yields little/no text (i.e. it's a scanned image), rasterize that
   page and run it through Tesseract OCR instead.
3. If the file is a plain image (png/jpg), go straight to Tesseract.
"""
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

from app.core.config import get_settings

settings = get_settings()

if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

MIN_CHARS_PER_PAGE = 20  # below this, assume the page is a scan and needs OCR

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_from_pdf(file_path)
    elif ext in IMAGE_EXTENSIONS:
        return _extract_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type for OCR: {ext}")


def _extract_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    full_text = []

    for page in doc:
        text = page.get_text().strip()

        if len(text) < MIN_CHARS_PER_PAGE:
            # Likely a scanned page - rasterize and OCR it
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)

        full_text.append(text)

    doc.close()
    return "\n\n".join(full_text).strip()


def _extract_from_image(file_path: str) -> str:
    img = Image.open(file_path)
    return pytesseract.image_to_string(img).strip()
