from typing import Any
import re


def _clean_highlight_text(text: str) -> str:
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

    fixes = [
        (r"\bem\s+ail\b", "email"),
        (r"\battem\s+pts\b", "attempts"),
        (r"\btem\s+porarily\b", "temporarily"),
        (r"\bcon\s*(?:firm|rm)\s*ation\b", "confirmation"),
        (r"\bautom\s*atically\b", "automatically"),
        (r"\bdocum\s*ents\b", "documents"),
        (r"\bdocum\s*ent\b", "document"),
        (r"\bm\s+ay\b", "may"),
    ]
    for pattern, repl in fixes:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def format_sources(docs: list[Any], max_sources: int = 2) -> list[dict]:
    sources = []
    seen = set()

    for doc in docs:
        metadata = getattr(doc, "metadata", {}) or {}
        source_name = metadata.get("source_name") or metadata.get(
            "file_name", "Unknown source"
        )
        source_type = metadata.get("source_type", "unknown")
        page = metadata.get("page")
        section_title = metadata.get("section_title")

        key = (source_name, source_type, page, section_title)
        if key in seen:
            continue
        seen.add(key)

        item = {
            "source_name": source_name,
            "source_type": source_type,
        }
        if page is not None:
            item["page"] = page + 1
        if section_title:
            item["section_title"] = section_title

        sources.append(item)
        if len(sources) >= max_sources:
            break

    return sources


def format_highlights(
    docs: list[Any], max_items: int = 2, max_chars: int = 260
) -> list[dict]:
    highlights = []
    seen = set()

    for doc in docs:
        metadata = getattr(doc, "metadata", {}) or {}
        text = _clean_highlight_text(getattr(doc, "page_content", "").strip())
        if len(text) < 40:
            continue

        source_name = metadata.get("source_name") or metadata.get(
            "file_name", "Unknown source"
        )
        source_type = metadata.get("source_type", "unknown")
        page = metadata.get("page")
        section_title = metadata.get("section_title")

        key = (source_name, source_type, page, section_title)
        if key in seen:
            continue
        seen.add(key)

        if len(text) > max_chars:
            text = text[:max_chars].rstrip() + "..."

        item = {
            "source_name": source_name,
            "source_type": source_type,
            "text": text,
        }
        if page is not None:
            item["page"] = page + 1
        if section_title:
            item["section_title"] = section_title

        highlights.append(item)
        if len(highlights) >= max_items:
            break

    return highlights
