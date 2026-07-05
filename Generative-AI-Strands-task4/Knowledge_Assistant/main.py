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