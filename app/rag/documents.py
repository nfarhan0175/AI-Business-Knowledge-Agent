from pathlib import Path
from pypdf import PdfReader

DOCUMENTS_DIR = Path("data/documents")
PDF_PATH = DOCUMENTS_DIR / "olist_business_guide.pdf"

def clean_pdf_text(text):
    lines = [line.strip() for line in text.splitlines()]
    cleaned_lines = []
    for line in lines:
        if not line:
            cleaned_lines.append("")
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    text = " ".join(text.split())
    return text.strip()

def load_pdf_documents():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF file not found: {PDF_PATH}")
    reader = PdfReader(PDF_PATH)
    documents = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if not text:
            continue
        # text = text.strip()
        text = clean_pdf_text(text)
        documents.append({
            "id": f"pdf_page_{page_number}",
            "text": text,
            "metadata": {
                "source": "olist_business_guide.pdf",
                "page": page_number
            }
        })
    return documents

if __name__ == "__main__":
    documents = load_pdf_documents()
    print("Total pages:", len(documents))
    if documents:
        print("\nFirst page:")
        print(documents[0]["text"])

        print("\nMetadata:")
        print(documents[0]["metadata"])