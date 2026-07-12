from strands import tool
from config import AWS_REGION, EMBED_MODEL_ID, EMBED_DIM
from Ingestion.vector_store import VectorStore

try:
    from Ingestion.embeddings import embed_batch
except ImportError:  # pragma: no cover - fallback for environments without the module
    import json
    import numpy as np
    import boto3

    _bedrock_client = None

    def _client():
        global _bedrock_client
        if _bedrock_client is None:
            _bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
        return _bedrock_client

    def embed_text(text: str) -> np.ndarray:
        body = json.dumps({"inputText": text, "dimensions": EMBED_DIM, "normalize": True})
        response = _client().invoke_model(
            modelId=EMBED_MODEL_ID,
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(response["body"].read())
        return np.array(payload["embedding"], dtype="float32")
else:
    from Ingestion.embeddings import embed_text

_store = VectorStore()


def retrieve(query: str, top_k: int = 4) -> list:
    """Embed `query` and return the top_k most similar chunks as dicts."""
    query_vector = embed_text(query)
    return _store.search(query_vector, top_k=top_k)



@tool(name="retrieve", description="Search the vector database for relevant document chunks and return them as formatted evidence.")
def retrieve_and_format(query: str, top_k: int = 4) -> str:
    """Embed `query` and return the top_k most similar chunks as formatted text."""
    results = retrieve(query, top_k=top_k)
    return format_results(results)


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


