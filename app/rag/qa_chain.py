# from typing import List
# from langchain_core.documents import Document


# def generate_answer(query: str, docs: List[Document]) -> str:
#     """
#     Generate a simple grounded answer from retrieved documents.
#     """

#     if not docs:
#         return "This information is not found in the documents."

#     best_doc = min(docs, key=lambda d: d.metadata.get("score", 999.0))
#     best_score = best_doc.metadata.get("score", 999.0)

#     if best_score > 0.70:
#         return "This information is not found in the documents."

#     snippet = best_doc.page_content.strip().replace("\n", " ")
#     source_name = best_doc.metadata.get("file_name", "unknown source")
#     page = best_doc.metadata.get("page", None)

#     answer = "Based on the available documents:\n\n"
#     answer += snippet[:400] + "...\n\n"
#     answer += f"Source: {source_name}"

#     if page is not None:
#         answer += f" | Page: {page + 1}"

#     return answer


# =================================================

# from typing import List
# from langchain_core.documents import Document


# def generate_answer(query: str, docs: List[Document]) -> str:

#     if not docs:
#         return "This information is not found in the documents."

#     best_doc = docs[0]

#     snippet = best_doc.page_content.strip().replace("\n", " ")

#     source_name = best_doc.metadata.get("file_name", "unknown source")
#     page = best_doc.metadata.get("page", None)

#     # 🔥 format answer
#     answer = "📌 Answer:\n\n"

#     # حاول تقطع الجملة بشكل منطقي
#     sentences = snippet.split(". ")

#     for s in sentences[:3]:
#         answer += f"- {s.strip()}\n"

#     answer += "\n📄 Source:\n"
#     answer += f"- File: {source_name}\n"

#     if page is not None:
#         answer += f"- Page: {page + 1}\n"

#     return answer

# ====================================================
# from typing import List
# from langchain_core.documents import Document


# def clean_text(text: str) -> str:
#     text = text.replace("\n", " ")
#     text = text.replace("�", "")
#     text = text.replace(".md", "")
#     text = text.replace(".pdf", "")
#     text = " ".join(text.split())
#     return text.strip()


# def generate_answer(query: str, docs: List[Document]) -> str:
#     if not docs:
#         return "❌ This information is not found in the documents."

#     best_doc = docs[0]

#     snippet = clean_text(best_doc.page_content)

#     source_name = best_doc.metadata.get("file_name", "unknown source")
#     page = best_doc.metadata.get("page", None)

#     # 🧠 حاول تطلع فكرة مش copy paste
#     answer = "📌 **Answer:**\n\n"

#     # بدل ما تقسم بالجمل، ناخد chunk كويس
#     answer += snippet[:300] + "...\n\n"

#     # 🔥 Source واضح
#     answer += "📄 **Source:**\n"
#     answer += f"- File: `{source_name}`\n"

#     if page is not None:
#         answer += f"- Page: {page + 1}\n"

#     return answer

# ====================================================
import re
from typing import List
from langchain_core.documents import Document

UNKNOWN_RESPONSE = "This information is not found in the documents."


def _clean_snippet(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "\ufffd": " ",
        "�": " ",
        "￾": "fi",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("\n", " ")
    text = re.sub(r"\S+\.md", "", text)
    text = re.sub(r"\S+\.pdf", "", text)
    text = re.sub(r"\d{4}-\d{2}-\d{2}", "", text)

    fixes = [
        (r"\bem\s+ail\b", "email"),
        (r"\battem\s+pts\b", "attempts"),
        (r"\btem\s+porarily\b", "temporarily"),
        (r"\bcon\s*(?:firm|rm)\s*ation\b", "confirmation"),
        (r"\bcon\s*firm\b", "confirm"),
        (r"\bveri\s*fication\b", "verification"),
        (r"\bnoti\s*fication\b", "notification"),
        (r"\bautom\s*atically\b", "automatically"),
        (r"\bdocum\s*ent\b", "document"),
        (r"\bdocum\s*ents\b", "documents"),
        (r"\bunlim\s*ited\b", "unlimited"),
        (r"\bintegr\s*ations\b", "integrations"),
        (r"\bperm\s*issions\b", "permissions"),
        (r"\badmin\s*istrative\b", "administrative"),
        (r"\bcom\s*pliance\b", "compliance"),
        (r"\bfi\s*le\b", "file"),
        (r"\bfi\s*les\b", "files"),
        (r"\bm\s+ay\b", "may"),
    ]
    for pattern, repl in fixes:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    # insert sentence boundaries for common headings embedded inside extracted PDF text
    heading_patterns = [
        "Password Reset",
        "Email Verification",
        "Two-Factor Authentication",
        "Workspaces",
        "Available Plans",
        "Free Plan",
        "Pro Plan",
        "Enterprise Plan",
        "Free Trial",
        "Billing Cycle",
        "Source Citation",
        "Evidence Highlighting",
        "Unknown Handling",
    ]
    for heading in heading_patterns:
        text = re.sub(rf"(?<![.!?])\s+({re.escape(heading)})\b", r". \1", text)

    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _intent(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["password", "reset", "forgot", "login"]):
        return "password"
    if any(w in q for w in ["pricing", "plan", "plans", "price", "subscription"]):
        return "pricing"
    if any(w in q for w in ["feature", "features", "provide", "service"]):
        return "features"
    return "general"


def _score_sentence(sentence: str, query: str, intent: str) -> int:
    lowered = sentence.lower()
    raw_query_words = set(re.findall(r"\w+", query.lower()))
    score = sum(1 for w in raw_query_words if w in lowered)

    if intent == "password":
        positive = [
            "forgot password",
            "password reset",
            "reset link",
            "login screen",
            "registered email",
        ]
        negative = [
            "failed login attempts",
            "suspicious logins",
            "period of inactivity",
        ]
        score += 3 * sum(1 for p in positive if p in lowered)
        score -= 2 * sum(1 for n in negative if n in lowered)
    elif intent == "pricing":
        positive = [
            "free",
            "pro",
            "enterprise",
            "price",
            "$19",
            "custom pricing",
            "three main plans",
        ]
        score += 2 * sum(1 for p in positive if p in lowered)
    elif intent == "features":
        positive = [
            "document upload",
            "website knowledge",
            "source citation",
            "evidence highlighting",
            "conversation memory",
            "category-aware retrieval",
            "admin controls",
            "analytics",
            "logs",
            "ai-powered question answering",
        ]
        score += 2 * sum(1 for p in positive if p in lowered)

    if len(sentence) < 25:
        score -= 2

    return score


def generate_answer(query: str, docs: List[Document]) -> str:
    if not docs:
        return UNKNOWN_RESPONSE

    best_doc = docs[0]
    semantic_distance = float(best_doc.metadata.get("semantic_distance", 999.0))
    final_score = float(best_doc.metadata.get("final_score", 0.0))

    if semantic_distance > 0.75 or final_score < 0.15:
        return UNKNOWN_RESPONSE

    cleaned_text = _clean_snippet(best_doc.page_content)
    if len(cleaned_text) < 30:
        return UNKNOWN_RESPONSE

    sentences = _split_sentences(cleaned_text)
    if not sentences:
        return UNKNOWN_RESPONSE

    intent = _intent(query)
    ranked = sorted(
        ((_score_sentence(s, query, intent), s) for s in sentences),
        key=lambda x: x[0],
        reverse=True,
    )

    selected: list[str] = []
    seen = set()
    max_points = 2 if intent in {"password", "pricing", "features"} else 3

    for score, sentence in ranked:
        normalized = sentence.lower()
        if score < 1 or normalized in seen:
            continue
        seen.add(normalized)
        selected.append(sentence)
        if len(selected) >= max_points:
            break

    if not selected:
        return UNKNOWN_RESPONSE

    return "\n".join(f"- {sentence}" for sentence in selected)
