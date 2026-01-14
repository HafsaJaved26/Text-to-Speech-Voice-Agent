import os
import re
import easyocr
import fitz  # PyMuPDF
from PIL import Image

# Initialize EasyOCR once (English + Urdu)
reader = easyocr.Reader(['en', 'ur'], gpu=False)


def clean_text(text):
    """
    Minimal cleaning only (task-safe)
    """
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


# -----------------------------
# IMAGE OCR
# -----------------------------
def extract_text_from_image(image_path):
    """
    Extract text from image (English or Urdu)
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


# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(pdf_path):
    """
    Extract text from PDF.
    If page has no text, apply OCR (scanned PDF).
    """
    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError("Unsupported PDF format")

    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        page_text = page.get_text()

        # If scanned page → OCR
        if not page_text.strip():
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            # OCR on rendered page image
            results = reader.readtext(
                img,
                detail=0,
                paragraph=True
            )
            page_text = "\n".join(results)

        full_text.append(page_text)

    return clean_text("\n".join(full_text))


# -----------------------------
# SINGLE ENTRY POINT
# -----------------------------
def extract_text(file_path):
    """
    Unified function:
    Works for images and PDFs
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError("File not found")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".png", ".jpg", ".jpeg", ".webp"]:
        return extract_text_from_image(file_path)

    elif ext == ".pdf":
        return extract_text_from_pdf(file_path)

    else:
        raise ValueError("Unsupported file type")


# -----------------------------
# COLAB / LOCAL RUN
# -----------------------------
if __name__ == "__main__":
    file_name = input("Enter image or PDF file name: ").strip()

    try:
        text = extract_text(file_name)

        print("\n========== EXTRACTED TEXT ==========\n")
        print(text)
        print("\n===================================")

    except Exception as e:
        print(f"\n❌ Error: {e}")
