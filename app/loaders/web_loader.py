from pathlib import Path
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from app.utils.text_cleaning import clean_extracted_text


def load_html_files(web_dir: Path) -> list[Document]:
    documents = []

    html_files = list(web_dir.glob("*.html"))

    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        text = soup.get_text(separator="\n", strip=True)
        text = clean_extracted_text(text)

        doc = Document(
            page_content=text,
            metadata={
                "source_type": "web",
                "file_name": html_file.name,
                "source_name": html_file.name,
                "source": str(html_file),
                "section_title": title,
            },
        )

        documents.append(doc)

    return documents
