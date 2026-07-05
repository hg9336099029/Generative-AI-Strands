# app/tools.py
# ------------
# Strands tool definitions. Currently just retrieve_knowledge, which wraps
# app.retrieval so the agent can call it. Kept as its own module so adding
# more tools later (e.g. a re-ranker, a citation-checker) doesn't bloat
# agent.py.

from strands import tool
from .config import DEFAULT_TOP_K
from .retrieval import retrieve_and_format


@tool
def retrieve_knowledge(query: str, top_k: int = DEFAULT_TOP_K) -> str:
    
    """Search the knowledge base for chunks relevant to a query.
    Use this whenever you need facts from the document set to answer the
    user's question. If the results don't fully answer the question,
    call this again with a more specific or differently-worded query
    before giving up.

    Args:
        query: A natural-language search query (the user's question, or
            a reformulation/sub-question of it).
        top_k: How many chunks to return, ranked by similarity.

    Returns:
        A formatted string listing each matching chunk with its source
        file, page/section, and similarity score. Returns a clear
        "no results" message if nothing matches.
    """

    return retrieve_and_format(query, top_k=top_k)