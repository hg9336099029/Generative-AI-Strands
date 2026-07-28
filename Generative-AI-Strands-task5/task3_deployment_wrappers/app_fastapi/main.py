# To run: uvicorn app_fastapi:api --port 8000
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
from app import agent   

app = FastAPI(title="Strands Agent Server", version="1.0.0")


class InvocationRequest(BaseModel):
    input: Dict[str, Any]


class InvocationResponse(BaseModel):
    output: Dict[str, Any]


@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """
    Required by AgentCore Runtime contract: POST endpoint for agent interactions.
    """
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="No prompt found in input.")

        result = agent(user_message)

        return InvocationResponse(
            output={
                "message": result.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": "strands-agent",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ping")
async def ping():
    """
    Required by AgentCore Runtime contract: GET health check endpoint.
    Returns "Healthy" or "HealthyBusy" per the documented status values.
    """
    return {
        "status": "Healthy",
        "time_of_last_update": int(datetime.now(timezone.utc).timestamp()),
    }
