# =============================================================================
# KNOWLEDGE ASSISTANT - COMPLETE FLOW
# =============================================================================
#
# 1. User sends a request:
#
#       POST /ask
#       {
#           "question": "What is RAG?"
#       }
#
# -----------------------------------------------------------------------------
#
# 2. FastAPI receives the request.
#
#       agent = get_agent()
#
#    • get_agent() ONLY creates (or reuses) the Agent.
#    • It does NOT receive or process the user's question.
#    • The Agent is cached so it is not rebuilt for every request.
#
# -----------------------------------------------------------------------------
#
# 3. If the Agent does not exist:
#
#       build_agent()
#
#    build_agent() configures the Agent by attaching:
#
#       ✓ Bedrock Claude Model
#       ✓ retrieve_knowledge Tool
#       ✓ System Prompt
#
#    No user question is passed here because the Agent is only being created.
#
# -----------------------------------------------------------------------------
#
# 4. Ask the Agent:
#
#       result = agent(request.question)
#
#    This is where the user's question is finally passed to the Agent.
#
#    Example:
#
#       agent("Explain Retrieval-Augmented Generation")
#
# -----------------------------------------------------------------------------
#
# 5. Agent starts reasoning.
#
#    Based on the System Prompt, the LLM decides:
#
#       • Can I answer directly?
#       • Do I need to search the knowledge base?
#
# -----------------------------------------------------------------------------
#
# 6. If retrieval is needed, the Agent automatically calls:
#
#       retrieve_knowledge(query)
#
#    IMPORTANT:
#
#       The Agent itself supplies 'query'.
#
#    The query may be:
#
#       • Original user question
#
#           "What is RAG?"
#
#       • Rewritten query
#
#           "Retrieval Augmented Generation"
#
#       • More specific query
#
#           "RAG architecture and workflow"
#
#    FastAPI never calls retrieve_knowledge().
#
# -----------------------------------------------------------------------------
#
# 7. retrieve_knowledge()
#
#       retrieve_knowledge(query)
#              │
#              ▼
#       retrieve_and_format(query)
#              │
#              ▼
#       Vector Database
#              │
#              ▼
#       Top-K Similar Chunks
#
# -----------------------------------------------------------------------------
#
# 8. Retrieved chunks are returned to the Agent.
#
#    The LLM reads those chunks, reasons over them,
#    cites sources if instructed, and generates the final answer.
#
# -----------------------------------------------------------------------------
#
# 9. FastAPI returns the response.
#
#       {
#           "question": "...",
#           "answer": "..."
#       }
#
# =============================================================================
# RESPONSIBILITY OF EACH FUNCTION
# =============================================================================
#
# build_agent()
# ----------------
# • Create and configure the Agent.
# • Attach Model + Tools + System Prompt.
# • Does NOT receive the user's question.
#
#
# get_agent()
# ----------------
# • Return the existing Agent if already created.
# • Otherwise build it once.
# • Does NOT execute the Agent.
#
#
# agent(question)
# ----------------
# • Execute the Agent.
# • User's question is passed here.
# • Starts reasoning and tool calling.
#
#
# retrieve_knowledge(query)
# -------------------------
# • Tool exposed to the Agent.
# • Called automatically by the Agent (not by FastAPI).
# • Searches the vector database.
# • Returns relevant document chunks.
#
#
# retrieve_and_format()
# ---------------------
# • Performs similarity search.
# • Formats retrieved chunks.
# • Returns them to the Agent.
#
# =============================================================================
# COMPLETE FLOW
# =============================================================================
#
# User
#   │
#   ▼
# POST /ask
#   │
#   ▼
# get_agent()
#   │
#   ▼
# build_agent()      (Only once)
#   │
#   ▼
# Agent
#   │
#   ▼
# agent(question)
#   │
#   ▼
# LLM Reasoning
#   │
#   ├──────────────► retrieve_knowledge(query)
#   │                     │
#   │                     ▼
#   │              Vector Database
#   │                     │
#   │                     ▼
#   │              Retrieved Chunks
#   │
#   ▼
# Final Answer
#   │
#   ▼
# FastAPI Response
#
# =============================================================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agent import build_agent

app = FastAPI(
    title="Knowledge Assistant",
    description="Agentic RAG over your document set, built on the Strands Agents SDK.",
    version="1.0.0",
)

_agent = None  


def get_agent():

    """Build the agent once and reuse it across requests. Deferred so
    importing this module (e.g. for tests) doesn't require AWS
    credentials or a live Bedrock connection."""

    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask the assistant.")


class AskResponse(BaseModel):
    question: str
    answer: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    
    """Ask the Knowledge Assistant a question. It will retrieve from the
    document set (retrying with refined queries if needed) and return a
    grounded, cited answer, or say it couldn't find one."""

    try:

        agent = get_agent()
        result = agent(request.question)
    except FileNotFoundError as e:
        # Raised by the vector store if ingest.py hasn't been run yet.
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return AskResponse(question=request.question, answer=str(result))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)