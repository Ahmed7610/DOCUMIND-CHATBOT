import streamlit as st

from app.loaders.loader_manager import load_all_documents
from app.rag.chunker import split_documents
from app.rag.embeddings_store import build_vector_store, load_vector_store
from app.rag.retriever import retrieve_documents
from app.rag.qa_chain import generate_answer
from app.rag.guardrails import UNKNOWN_RESPONSE, has_relevant_results, is_unknown_answer
from app.rag.response_formatter import format_sources, format_highlights
from app.utils.config import CHROMA_DIR


@st.cache_resource
def load_rag_pipeline():
    """
    Build or load the RAG pipeline once and cache it for Streamlit.
    """
    if CHROMA_DIR.exists():
        vector_store = load_vector_store()
        documents = None
        chunks = None
        store_status = "Loaded existing Chroma DB"
    else:
        documents = load_all_documents()
        chunks = split_documents(documents)
        vector_store = build_vector_store(chunks)
        store_status = "Built new Chroma DB"

    return {
        "vector_store": vector_store,
        "documents": documents,
        "chunks": chunks,
        "store_status": store_status,
    }


def answer_question(query: str, top_k: int = 2, max_distance: float = 0.65) -> dict:
    """
    Run retrieval + grounded answer generation for a user query.
    """
    pipeline = load_rag_pipeline()

    results = retrieve_documents(
        vector_store=pipeline["vector_store"],
        query=query,
        top_k=top_k,
        max_distance=max_distance,
    )

    if not has_relevant_results(results):
        return {
            "answer": UNKNOWN_RESPONSE,
            "sources": [],
            "highlights": [],
            "is_unknown": True,
            "results": results,
        }

    answer = generate_answer(query, results)

    if is_unknown_answer(answer):
        return {
            "answer": UNKNOWN_RESPONSE,
            "sources": [],
            "highlights": [],
            "is_unknown": True,
            "results": results,
        }

    return {
        "answer": answer,
        "sources": format_sources(results, max_sources=3),
        "highlights": format_highlights(results, max_items=3),
        "is_unknown": False,
        "results": results,
    }
