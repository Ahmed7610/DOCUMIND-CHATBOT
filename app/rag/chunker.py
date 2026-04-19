from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(
    documents: list[Document], chunk_size: int = 700, chunk_overlap: int = 120
) -> list[Document]:
    """
    Split loaded documents into smaller chunks for embedding and retrieval.

    Args:
        documents: List of LangChain Document objects.
        chunk_size: Maximum size of each chunk in characters.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        List of chunked Document objects.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],  # what means of that
    )

    chunks = text_splitter.split_documents(
        documents
    )  # explain this how i use the model i define inside the function then use the function

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i

    return chunks
