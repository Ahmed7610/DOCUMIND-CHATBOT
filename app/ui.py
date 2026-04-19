import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.rag_pipeline import answer_question, load_rag_pipeline

st.set_page_config(
    page_title="AI Career Project - Document Assistant", page_icon="💬", layout="wide"
)

pipeline = load_rag_pipeline()

st.title("🧠 DocuMind AI – Intelligent Document Assistant")
st.caption("Ask questions about the available PDF and website documents.")

with st.sidebar:
    st.header("System Info")
    st.write("UI: Streamlit")
    st.write("Sources: PDF + HTML")
    st.write("Vector DB: Chroma")
    st.write("Retrieval: Hybrid (Semantic + TF-IDF)")
    st.write(f"Status: {pipeline['store_status']}")

    if pipeline["documents"] is not None:
        st.write(f"Documents loaded: {len(pipeline['documents'])}")

    if pipeline["chunks"] is not None:
        st.write(f"Chunks created: {len(pipeline['chunks'])}")

    if st.button("Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! Ask me anything about the available documents.",
                "sources": [],
                "highlights": [],
            }
        ]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! Ask me anything about the available documents.\n\n"
                "Examples:\n"
                "- What pricing plans are available?\n"
                "- How can I reset my password?\n"
                "- What features does the service provide?"
            ),
            "sources": [],
            "highlights": [],
        }
    ]


def render_sources(sources: list[dict]):
    if not sources:
        return

    st.markdown("**Sources**")
    for src in sources:
        label = src["source_name"]

        if src.get("page") is not None:
            label += f" — Page {src['page']}"
        elif src.get("section_title"):
            label += f" — {src['section_title']}"

        st.markdown(f"- {label}")


def render_highlights(highlights: list[dict]):
    if not highlights:
        return

    st.markdown("**Relevant Text Used**")
    for item in highlights:
        title = item["source_name"]

        if item.get("page") is not None:
            title += f" — Page {item['page']}"
        elif item.get("section_title"):
            title += f" — {item['section_title']}"

        with st.expander(title):
            st.write(item["text"])


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_sources(message.get("sources", []))
        render_highlights(message.get("highlights", []))

user_query = st.chat_input("Ask your question...")

if user_query:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query,
            "sources": [],
            "highlights": [],
        }
    )

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            result = answer_question(user_query)

            answer = result["answer"]
            sources = result.get("sources", [])
            highlights = result.get("highlights", [])

            st.markdown(answer)
            render_sources(sources)
            render_highlights(highlights)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "highlights": highlights,
        }
    )
