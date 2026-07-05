# app/retrieval.py
# -----------------
# Query-time retrieval logic: embed the query, search the vector store,
# and format results into a string an LLM can read. Kept separate from
# app/tools.py so this logic is reusable/testable without going through
# the Strands @tool wrapper (e.g. from a notebook or a unit test).

from .embeddings import embed_text
from .vector_store import VectorStore

_store = VectorStore()


def retrieve(query: str, top_k: int = 4) -> list:
    """Embed `query` and return the top_k most similar chunks (as dicts)."""
    query_vector = embed_text(query)
    return _store.search(query_vector, top_k=top_k)


def format_results(results: list) -> str:
    """Render retrieval results as a citation-friendly string for the LLM."""
    if not results:
        return "No relevant chunks were found in the knowledge base for this query."

    lines = []

    for i, result in enumerate(results, start=1):
        metadata_parts = []
        if result.get("source"):
            metadata_parts.append(f"source: {result['source']}")
        if result.get("page") not in (None, ""):
            metadata_parts.append(f"page: {result['page']}")
        if result.get("section"):
            metadata_parts.append(f"section: {result['section']}")

        metadata_text = " | ".join(metadata_parts) if metadata_parts else "metadata: unavailable"
        score_text = f" | score: {result.get('score', 0):.3f}" if result.get("score") is not None else ""

        lines.append(
            f"[{i}] {metadata_text}{score_text}\n"
            f"{result.get('text', '')}\n"
        )

    return "\n".join(lines)


def retrieve_and_format(query: str, top_k: int = 4) -> str:
    return format_results(retrieve(query, top_k=top_k))