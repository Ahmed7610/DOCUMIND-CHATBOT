# # Library for not duplicating
# import shutil
# from pathlib import Path

# # Embeddings Library
# from langchain_community.embeddings import FastEmbedEmbeddings
# from langchain_chroma import Chroma
# from langchain_core.documents import Document

# from app.utils.config import CHROMA_DIR


# def build_vector_store(chunks: list[Document]) -> Chroma:
#     """
#     Create a fresh Chroma vector store using local FastEmbed embeddings.
#     If an old DB exists, remove it first to avoid duplicate chunks.
#     """
#     if CHROMA_DIR.exists():
#         shutil.rmtree(CHROMA_DIR)

#     embeddings = FastEmbedEmbeddings()
#     ids = [
#         f"{chunk.metadata.get('file_name', 'unknown')}_"
#         f"{chunk.metadata.get('page', 'na')}_"
#         f"{chunk.metadata.get('chunk_id', i)}"
#         for i, chunk in enumerate(chunks)
#     ]  # what is that

#     vector_store = Chroma.from_documents(
#         documents=chunks,
#         embedding=embeddings,
#         ids=ids,
#         persist_directory=str(CHROMA_DIR),
#     )

#     return vector_store


# def load_vector_store() -> Chroma:
#     """
#     Load an existing Chroma vector store from disk.
#     """
#     embeddings = FastEmbedEmbeddings()

#     vector_store = Chroma(
#         persist_directory=str(CHROMA_DIR),
#         embedding_function=embeddings,
#     )

#     return vector_store


import shutil
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.utils.config import CHROMA_DIR


def build_vector_store(chunks: list[Document]) -> Chroma:
    """
    Create a fresh Chroma vector store using local FastEmbed embeddings.
    If an old DB exists, remove it first to avoid duplicate chunks.
    """
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    embeddings = FastEmbedEmbeddings()

    ids = [
        f"{chunk.metadata.get('file_name', 'unknown')}_"
        f"{chunk.metadata.get('page', 'na')}_"
        f"{chunk.metadata.get('chunk_id', i)}"
        for i, chunk in enumerate(chunks)
    ]

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        ids=ids,
        persist_directory=str(CHROMA_DIR),
    )

    return vector_store


def load_vector_store() -> Chroma:
    """
    Load an existing Chroma vector store from disk.
    """
    embeddings = FastEmbedEmbeddings()

    vector_store = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    return vector_store
