import os
import re
import pdfplumber
import fitz  # PyMuPDF
import easyocr
from PIL import Image
from docx import Document

# -------------------------------------------------
# Initialize EasyOCR once (English + Urdu)
# -------------------------------------------------
reader = easyocr.Reader(['en', 'ur'], gpu=False)


# -------------------------------------------------
# TEXT CLEANING
# -------------------------------------------------
def clean_text(text):
    """
    Minimal, safe text cleaning
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


# -------------------------------------------------
# DOCX TEXT EXTRACTION
# -------------------------------------------------
def extract_text_from_docx(docx_path):
    """
    Extract text from DOCX file
    """
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return clean_text(text)


# -------------------------------------------------
# IMAGE OCR
# -------------------------------------------------
def extract_text_from_image(image_path):
    """
    OCR for images (English + Urdu)
    """
    if not image_path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        raise ValueError("Unsupported image format")

    results = reader.readtext(
        image_path,
        detail=0,
        paragraph=True
    )

    text = "\n".join(results)
    return clean_text(text)


# -------------------------------------------------
# PDF TEXT EXTRACTION (TEXT + OCR FALLBACK)
# -------------------------------------------------
def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF.
    Uses:
    - pdfplumber for normal text PDFs
    - EasyOCR for scanned PDFs
    """
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("Unsupported PDF format")

    full_text = []

    # First try normal text extraction
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text.append(page_text)
    except Exception:
        pass

    # If text found → return
    if full_text:
        return clean_text("\n".join(full_text))

    # Otherwise → OCR scanned PDF
    doc = fitz.open(pdf_path)

    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        results = reader.readtext(
            img,
            detail=0,
            paragraph=True
        )
        full_text.append("\n".join(results))

    return clean_text("\n".join(full_text))


# -------------------------------------------------
# SINGLE UNIFIED ENTRY POINT
# -------------------------------------------------
def extract_text(file_path):
    """
    Works for:
    - PDF (text + scanned)
    - DOCX
    - Images
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    elif ext == ".docx":
        return extract_text_from_docx(file_path)

    elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
        return extract_text_from_image(file_path)

    else:
        raise ValueError("Unsupported file type")
