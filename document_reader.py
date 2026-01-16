# document_reader.py
import pdfplumber
from docx import Document

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using pdfplumber
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    """
    Extract text from a DOCX file using python-docx
    """
    text = ""
    try:
        doc = Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX: {e}")
    return text

def extract_text(source):
    """
    Unified function to detect file type and extract text
    """
    if source.lower().endswith(".pdf"):
        return extract_text_from_pdf(source)
    elif source.lower().endswith(".docx"):
        return extract_text_from_docx(source)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")

def normalize_text(text):
    """
    Basic text cleaning: remove extra spaces and blank lines
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

# Example usage
if __name__ == "__main__":
    file_path = input("Enter file path (PDF or DOCX): ")
    try:
        raw_text = extract_text(file_path)
        clean_text = normalize_text(raw_text)
        print("\nExtracted Text:\n")
        print(clean_text)
    except Exception as e:
        print(f"Failed to extract text: {e}")
