from __future__ import annotations

from unicodedata import normalize


def build_fts_ngram_text(text: str | None, gram_size: int = 2) -> str:
    """Build an n-gram token string for FTS indexing and querying.

    The result is a space-separated list of overlapping character n-grams.
    Short strings are returned as-is so single-character names still work.
    """
    if not text:
        return ""

    normalized = normalize("NFC", text)
    normalized = " ".join(normalized.split())

    if len(normalized) <= gram_size:
        return normalized

    return " ".join(
        normalized[index:index + gram_size]
        for index in range(len(normalized) - gram_size + 1)
    )
