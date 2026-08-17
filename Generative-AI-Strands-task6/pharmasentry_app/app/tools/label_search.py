"""
Retrieval over the indexed labelling corpus for LabelAgent.

This is deliberately separate from openfda_tool.openfda_label_search: that
tool hits the live openFDA API for a single section of a single product;
this tool retrieves the best-matching *chunks* from the curated, scoped
corpus in data/labels/ (built by scripts/build_label_index.py) so the agent
can cite a specific passage rather than a whole label section. Using both
gives LabelAgent a fast local grounding source plus a live cross-check.

Gracefully returns {"found": False, "reason": ...} when:
  - rank_bm25 is not installed
  - the index file hasn't been built yet
so the rest of the pipeline never hard-crashes.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from strands import tool

from app.config import settings

INDEX_PATH = Path(settings.label_index_path)

_bm25 = None
_chunks: list[dict] | None = None
_index_unavailable_reason: str | None = None


def _load_index():
    global _bm25, _chunks, _index_unavailable_reason

    if _bm25 is not None and _chunks is not None:
        return _bm25, _chunks

    if _index_unavailable_reason:
        return None, None

    # Check for rank_bm25
    try:
        from rank_bm25 import BM25Okapi  # noqa: F401
    except ImportError:
        _index_unavailable_reason = "rank_bm25 not installed"
        return None, None

    if not INDEX_PATH.exists():
        _index_unavailable_reason = (
            f"Label index not found at {INDEX_PATH}. "
            "Run `python scripts/build_label_index.py` first."
        )
        return None, None

    try:
        from rank_bm25 import BM25Okapi

        with open(INDEX_PATH, encoding="utf-8") as f:
            payload = json.load(f)

        _chunks = payload.get("chunks", [])
        if not _chunks:
            _index_unavailable_reason = "Label index is empty."
            return None, None

        tokenized = [c["text"].lower().split() for c in _chunks]
        _bm25 = BM25Okapi(tokenized)
        return _bm25, _chunks
    except Exception as exc:
        _index_unavailable_reason = f"Failed to load label index: {exc}"
        return None, None


@tool
def label_corpus_search(query: str, product_name: str | None = None, top_k: int = 3) -> dict[str, Any]:
    """
    Retrieve the best-matching passages from the indexed, approved-labelling
    corpus (scoped to the capstone's chosen products: lisinopril, metformin,
    sertraline).

    Args:
        query: The user's question or a reformulation of it.
        product_name: Optional filter, e.g. "lisinopril", to restrict results
            to one product's label.
        top_k: Number of passages to return (1-5).

    Returns:
        dict with keys: found, passages (list of {product, section, text,
        chunk_id, score}) — or found=False with reason if index unavailable.
    """
    bm25, chunks = _load_index()

    if bm25 is None or chunks is None:
        return {
            "found": False,
            "reason": _index_unavailable_reason or "Label index unavailable.",
        }

    candidate_idx = list(range(len(chunks)))
    if product_name:
        candidate_idx = [
            i for i in candidate_idx if chunks[i]["product"].lower() == product_name.lower()
        ]
        if not candidate_idx:
            return {"found": False, "reason": f"No indexed label for product '{product_name}'."}

    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    ranked = sorted(candidate_idx, key=lambda i: scores[i], reverse=True)[: max(1, min(top_k, 5))]
    passages = [
        {
            "product": chunks[i]["product"],
            "section": chunks[i]["section"],
            "text": chunks[i]["text"],
            "chunk_id": chunks[i]["chunk_id"],
            "score": round(float(scores[i]), 3),
        }
        for i in ranked
        if scores[i] > 0
    ]

    if not passages:
        return {"found": False, "reason": "No matching passages above relevance threshold."}

    return {"found": True, "passages": passages}