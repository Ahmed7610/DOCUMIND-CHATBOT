from langchain_core.documents import Document
from app.loaders.pdf_loader import load_pdfs
from app.loaders.web_loader import load_html_files
from app.utils.config import PDF_DIR, WEB_DIR


def load_all_documents() -> list[Document]:
    pdf_docs = load_pdfs(PDF_DIR)
    web_docs = load_html_files(WEB_DIR)

    all_docs = pdf_docs + web_docs  # Concatenation
    # all docs a new list have pdf_docs(each pdf page as a document) + web_docs (each html file as a document )
    return all_docs
