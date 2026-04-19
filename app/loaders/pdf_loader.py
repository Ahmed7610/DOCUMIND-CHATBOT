from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from app.utils.text_cleaning import clean_extracted_text


def load_pdfs(pdf_dir: Path) -> list[Document]:
    documents = []

    pdf_files = list(pdf_dir.glob("*.pdf"))

    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        for doc in docs:
            cleaned_text = clean_extracted_text(doc.page_content)

            # skip near-empty noisy pages
            if not cleaned_text or len(cleaned_text.strip()) < 20:
                continue

            doc.page_content = cleaned_text
            doc.metadata["source_type"] = "pdf"
            doc.metadata["file_name"] = pdf_file.name
            doc.metadata["source_name"] = pdf_file.name
            doc.metadata["source"] = str(pdf_file)

        documents.extend(docs)

    return documents
