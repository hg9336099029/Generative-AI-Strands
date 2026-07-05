# app/embeddings.py
# ------------------

# Amazon Titan Text Embeddings V2 client (via Bedrock). Kept isolated so
# the embedding model can be swapped (e.g. for an open-source
# sentence-transformers model) without touching ingestion or retrieval
# logic elsewhere.

import json
from typing import List
import boto3
import numpy as np
from .config import AWS_REGION, EMBED_MODEL_ID, EMBED_DIM

_bedrock_client = None


def _client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return _bedrock_client


def embed_text(text: str) -> np.ndarray:

    # Embed a single piece of text with Titan Text Embeddings V2.
    # Returns a normalized float32 vector (so cosine similarity == inner
    # product, which lets us use a plain FAISS IndexFlatIP).

    body = json.dumps(
        {
            "inputText": text,
            "dimensions": EMBED_DIM,
            "normalize": True,
        }
    )

    response = _client().invoke_model(
        modelId=EMBED_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    payload = json.loads(response["body"].read())
    return np.array(payload["embedding"], dtype="float32")


def embed_batch(texts: List[str]) -> np.ndarray:

    # Titan is invoked one text at a time; this loops and stacks the
    # results into a single (n, dim) matrix. Swap for a true batch call
    # if you move to a provider that supports it.
    
    if not texts:
        return np.zeros((0, EMBED_DIM), dtype="float32")
    return np.vstack([embed_text(t) for t in texts])