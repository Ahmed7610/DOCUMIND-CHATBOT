import re


def clean_extracted_text(text: str) -> str:
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

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)

    patterns = [
        (r"\bem\s+ail\b", "email"),
        (r"\battem\s+pts\b", "attempts"),
        (r"\btem\s+porarily\b", "temporarily"),
        (r"\bcon\s*(?:firm|rm)\s*ation\b", "confirmation"),
        (r"\bcon\s*firm\b", "confirm"),
        (r"\bveri\s*fication\b", "verification"),
        (r"\bnoti\s*fication\b", "notification"),
        (r"\bpro\s*file\b", "profile"),
        (r"\bautom\s*atically\b", "automatically"),
        (r"\bdocum\s*ent\b", "document"),
        (r"\bdocum\s*ents\b", "documents"),
        (r"\bunlim\s*ited\b", "unlimited"),
        (r"\bintegr\s*ations\b", "integrations"),
        (r"\bperm\s*issions\b", "permissions"),
        (r"\badmin\s*istrative\b", "administrative"),
        (r"\bcom\s*pliance\b", "compliance"),
        (r"\bwork\s*flow\b", "workflow"),
        (r"\bre\s*flect\b", "reflect"),
        (r"\bfi\s*le\b", "file"),
        (r"\bfi\s*les\b", "files"),
        (r"\bm\s+ay\b", "may"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"\s*([/(){}\[\]])\s*", r" \1 ", text)
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n +", "\n", text)

    return text.strip()
