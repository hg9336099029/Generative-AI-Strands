import json
from typing import List
import numpy as np
import boto3
from config import AWS_REGION, EMBED_MODEL_ID, EMBED_DIM

_bedrock_client = None


def _client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    return _bedrock_client


def embed_text(text: str) -> np.ndarray:
    """Embed a single text string using the Bedrock embedding model."""
    body = json.dumps({"inputText": text, "dimensions": EMBED_DIM, "normalize": True})
    response = _client().invoke_model(
        modelId=EMBED_MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    return np.array(payload["embedding"], dtype="float32")


def embed_batch(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, EMBED_DIM), dtype="float32")
    return np.vstack([embed_text(t) for t in texts])
