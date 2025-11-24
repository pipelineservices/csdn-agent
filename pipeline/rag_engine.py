# pipeline/rag_engine.py

import os
from typing import List, Dict, Any

# Project root = one level above "pipeline"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAG_DIR = os.path.join(BASE_DIR, "data", "rag")

# Simple config for our RAG docs
DOC_CONFIG = [
    {
        "id": "network_patterns",
        "domain": "network",
        "filename": "network_patterns.md",
        "title": "Network troubleshooting patterns",
    },
    {
        "id": "cloudhydra_patterns",
        "domain": "cloudhydra",
        "filename": "cloudhydra_patterns.md",
        "title": "Cloudhydra mesh connectivity patterns",
    },
    {
        "id": "tgx_troubleshooting",
        "domain": "network",
        "filename": "tgx_troubleshooting.md",
        "title": "Transit Gateway / TGW troubleshooting",
    },
    {
        "id": "databricks_connectivity",
        "domain": "cloudhydra",
        "filename": "databricks_connectivity.md",
        "title": "Databricks ↔ Aurora connectivity notes",
    },
]


def _load_text(path: str) -> str:
    """Safe file loader – returns empty string if not found."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _tokenize(text: str) -> set:
    """Very simple tokenization, enough for local RAG."""
    # You can make this smarter later (strip punctuation, etc.)
    return set(text.lower().replace("\n", " ").split())


def _score(query_tokens: set, doc_tokens: set) -> float:
    """Jaccard-like overlap score."""
    if not query_tokens or not doc_tokens:
        return 0.0
    overlap = len(query_tokens & doc_tokens)
    return overlap / len(query_tokens)


def search_rag(query: str, domain: str | None = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Tiny in-memory RAG:
    - loads docs from data/rag/*.md
    - scores by token overlap
    - returns top_k hits with snippet + score
    """
    query_tokens = _tokenize(query)
    hits: List[Dict[str, Any]] = []

    if not query_tokens:
        return []

    for cfg in DOC_CONFIG:
        if domain and cfg["domain"] != domain:
            continue

        path = os.path.join(RAG_DIR, cfg["filename"])
        text = _load_text(path)
        if not text.strip():
            continue

        doc_tokens = _tokenize(text)
        score = _score(query_tokens, doc_tokens)
        if score <= 0:
            continue

        hits.append(
            {
                "id": cfg["id"],
                "title": cfg["title"],
                "score": round(score, 4),
                "snippet": text[:500],  # first 500 chars
            }
        )

    hits.sort(key=lambda h: h["score"], reverse=True)
    return hits[:top_k]
