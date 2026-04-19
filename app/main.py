from app.loaders.loader_manager import load_all_documents
from app.rag.chunker import split_documents
from app.rag.embeddings_store import build_vector_store, load_vector_store
from app.rag.retriever import retrieve_documents
from app.rag.qa_chain import generate_answer
from app.utils.config import CHROMA_DIR


def main():
    rebuild = input("Do you want to rebuild the vector store? (y/n): ").strip().lower()

    if rebuild == "y":
        documents = load_all_documents()
        chunks = split_documents(documents)

        print(f"Total raw documents loaded: {len(documents)}")
        print(f"Total chunks created: {len(chunks)}")
        print("-" * 60)

        vector_store = build_vector_store(chunks)
        print(f"Vector store built and saved to: {CHROMA_DIR}")
    else:
        vector_store = load_vector_store()
        print(f"Loaded existing vector store from: {CHROMA_DIR}")

    while True:
        query = input("\nAsk your question (or type 'exit' to quit): ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        results = retrieve_documents(
            vector_store=vector_store,
            query=query,
            top_k=5,
            max_distance=0.78,
        )

        answer = generate_answer(query, results)

        print("\n" + "=" * 80)
        print("Answer:\n")
        print(answer)

        print("\nRetrieved Documents Preview:\n")
        if not results:
            print("No relevant documents passed the retrieval threshold.")
        else:
            for i, doc in enumerate(results, start=1):
                print(f"Result #{i}")
                print("Score:", round(doc.metadata.get("score", 0), 4))
                print("Source:", doc.metadata.get("file_name"))
                print("Page:", doc.metadata.get("page", "N/A"))
                print("Preview:", doc.page_content[:250].replace("\n", " "))
                print("-" * 80)


if __name__ == "__main__":
    main()
