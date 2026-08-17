from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, chat,cases, intake
from .database import engine, Base


app = FastAPI(
    title="PharmaSentry",
    description=(
        "A drug-safety and medical-information agent built with the Strands Agents SDK. "
        "Routes queries to three specialist agents (LabelAgent, SafetyAgent, TrialsAgent) "
        "using the agents-as-tools pattern, backed by AgentCore Memory (STM + LTM)."
    ),
    version="1.0.0",
)

# CORS — allow all origins for dev; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Create database tables on startup (graceful if DB unavailable)."""
    try:
        Base.metadata.create_all(bind=engine)
        print("[PharmaSentry] Database tables created / verified.")
    except Exception as exc:
        print(f"[PharmaSentry] Database initialization skipped (will retry on first request): {exc}")


@app.get("/ping", tags=["health"])
def ping():
    """
    Health-check endpoint.  AgentCore Runtime checks GET /ping to verify the
    container is alive before routing traffic.
    """
    return {"status": "ok", "service": "pharmasentry"}


@app.get("/", response_model=dict)
def root():
    """Root endpoint — welcome message."""
    return {
        "message": "Welcome to PharmaSentry — Drug Safety and Clinical Trial Information API",
        "docs": "/docs",
        "health": "/ping",
    }


# Include all routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(cases.router)
app.include_router(intake.router)