from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from tools.retrieval_tool import retrieve_and_format

app = FastAPI(
    title="Multi_Agent_Research",
    description="",
    version="1.0.0",
    )

multi_agent = None


def get_agent():
    """Return the retrieval-based agent wrapper used by the API."""
    global multi_agent
    if multi_agent is None:
        multi_agent = retrieve_and_format
    return multi_agent


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask the assistant.")


class AskResponse(BaseModel):
    question: str
    answer: str


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """ """
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