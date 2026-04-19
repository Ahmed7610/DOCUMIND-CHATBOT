# from langchain_core.documents import Document
# from langchain_chroma import Chroma


# def retrieve_documents(
#     vector_store: Chroma,
#     query: str,
#     top_k: int = 5,
#     max_distance: float = 0.78,
# ) -> list[Document]:
#     """
#     Retrieve top-k semantically similar documents from the vector store.

#     Lower score = better match in Chroma distance-based search.
#     We keep only documents below a chosen max_distance threshold.
#     """
#     query = query.strip().lower()

#     results = vector_store.similarity_search_with_score(query, k=top_k)

#     filtered_docs = []
#     seen = set()

#     for doc, score in results:
#         score = float(score)
#         doc.metadata["score"] = score

#         # deduplicate by source+page+chunk_id
#         key = (
#             doc.metadata.get("file_name"),
#             doc.metadata.get("page"),
#             doc.metadata.get("chunk_id"),
#         )
#         if key in seen:
#             continue
#         seen.add(key)

#         if score <= max_distance:
#             filtered_docs.append(doc)

#     # ensure best results come first
#     filtered_docs.sort(key=lambda d: d.metadata["score"])
#     return filtered_docs
# =======================================================
# from langchain_core.documents import Document
# from langchain_chroma import Chroma

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity


# def retrieve_documents(
#     vector_store: Chroma,
#     query: str,
#     top_k: int = 5,
#     max_distance: float = 0.70,
# ) -> list[Document]:

#     query = query.strip().lower()

#     results = vector_store.similarity_search_with_score(query, k=top_k)

#     # Extract docs + scores
#     docs = []
#     for doc, score in results:
#         doc.metadata["semantic_score"] = float(score)
#         docs.append(doc)

#     # 🔥 TF-IDF part
#     texts = [doc.page_content for doc in docs]

#     vectorizer = TfidfVectorizer()
#     tfidf_matrix = vectorizer.fit_transform(texts + [query])

#     query_vec = tfidf_matrix[-1]
#     doc_vecs = tfidf_matrix[:-1]

#     keyword_scores = cosine_similarity(query_vec, doc_vecs)[0]

#     # Combine scores
#     final_docs = []
#     seen = set()

#     for i, doc in enumerate(docs):
#         semantic = doc.metadata["semantic_score"]
#         keyword = keyword_scores[i]

#         # lower semantic = better → invert it
#         semantic_score = 1 - semantic

#         final_score = (0.6 * semantic_score) + (0.4 * keyword)

#         doc.metadata["final_score"] = final_score

#         key = (
#             doc.metadata.get("file_name"),
#             doc.metadata.get("page"),
#             doc.metadata.get("chunk_id"),
#         )

#         if key in seen:
#             continue
#         seen.add(key)

#         # فلترة semantic
#         if semantic <= max_distance:
#             final_docs.append(doc)

#     # ترتيب نهائي
#     final_docs.sort(key=lambda d: d.metadata["final_score"], reverse=True)

#     return final_docs


from langchain_core.documents import Document
from langchain_chroma import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_documents(
    vector_store: Chroma,
    query: str,
    top_k: int = 5,
    max_distance: float = 0.90,
) -> list[Document]:
    """
    Hybrid retrieval:
    1) semantic retrieval from Chroma
    2) keyword scoring with TF-IDF
    3) combine both into one final score
    """

    query = query.strip().lower()
    if not query:
        return []

    results = vector_store.similarity_search_with_score(query, k=top_k)

    if not results:
        return []

    docs = []
    for doc, distance in results:
        doc.metadata["semantic_distance"] = float(distance)
        docs.append(doc)

    texts = [doc.page_content for doc in docs]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts + [query])

    query_vec = tfidf_matrix[-1]
    doc_vecs = tfidf_matrix[:-1]

    keyword_scores = cosine_similarity(query_vec, doc_vecs)[0]

    final_docs = []
    seen = set()

    for i, doc in enumerate(docs):
        semantic_distance = doc.metadata["semantic_distance"]
        keyword_score = float(keyword_scores[i])

        # Convert distance to relevance-like score
        semantic_relevance = max(0.0, 1.0 - semantic_distance)

        final_score = (0.7 * semantic_relevance) + (0.3 * keyword_score)

        doc.metadata["keyword_score"] = keyword_score
        doc.metadata["semantic_relevance"] = semantic_relevance
        doc.metadata["final_score"] = final_score

        key = (
            doc.metadata.get("file_name"),
            doc.metadata.get("page"),
            doc.metadata.get("chunk_id"),
        )
        if key in seen:
            continue
        seen.add(key)

        # Keep only semantically acceptable candidates
        if semantic_distance <= max_distance:
            final_docs.append(doc)

    final_docs.sort(key=lambda d: d.metadata["final_score"], reverse=True)
    return final_docs
