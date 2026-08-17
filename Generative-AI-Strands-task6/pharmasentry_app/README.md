# 💊 PharmaSentry App

A multi-agent AI-powered pharmaceutical safety and compliance platform built with **AWS Strands Agents**, **FastAPI**, and **Amazon Bedrock**. PharmaSentry provides intelligent drug label analysis, clinical trial discovery, and medication safety monitoring through a network of specialized AI agents.

---

## 🚀 Features

- **🤖 Multi-Agent Architecture** — Supervisor, Label Analysis, Safety, and Clinical Trials agents working in coordination
- **🔒 PII Redaction** — Automatic detection and redaction of personally identifiable information before processing
- **🛡️ Guardrails** — Built-in safety guardrails powered by Amazon Bedrock
- **🔐 OAuth2 Authentication** — Secure JWT-based authentication and authorization
- **🧠 Memory / Context Management** — Persistent conversation memory across sessions
- **📋 Drug Label Analysis** — AI-powered analysis of FDA drug labels and package inserts
- **⚕️ Clinical Trials Discovery** — Automated search and summarization of relevant clinical trials
- **📊 REST API** — Full-featured FastAPI backend with OpenAPI documentation

---

## 🏗️ Architecture

```
pharmasentry_app/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # App configuration & environment settings
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── database.py             # Database connection & session management
│   ├── Oauth2.py               # OAuth2 / JWT authentication
│   ├── agent_client.py         # Agent gateway client
│   ├── gateway_target.py       # AgentCore gateway target integration
│   ├── pii_redaction.py        # PII detection & redaction utilities
│   ├── prompt_loader.py        # Dynamic prompt template loader
│   ├── utils.py                # Shared utility functions
│   ├── agents/
│   │   ├── supervisor.py       # Orchestrator / supervisor agent
│   │   ├── label_agent.py      # Drug label analysis agent
│   │   ├── safety_agent.py     # Medication safety agent
│   │   ├── trials_agent.py     # Clinical trials discovery agent
│   │   ├── model_provider.py   # Bedrock model provider & configuration
│   │   └── guardrails.py       # Bedrock guardrails integration
│   ├── routers/                # FastAPI route handlers
│   ├── tools/                  # Agent tools (FDA API, search, etc.)
│   ├── prompts/                # System prompt templates
│   └── memory/                 # Memory & context management
├── scripts/
│   └── test_local_agent.py     # Local agent testing script
├── data/                       # Data files and resources
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (not committed)
```

---

## ⚙️ Prerequisites

- Python **3.10+**
- AWS account with **Amazon Bedrock** access
- AWS CLI configured with appropriate credentials
- Access to **Claude** models on Amazon Bedrock (e.g., `claude-3-5-sonnet`)

---

## 🛠️ Setup & Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd pharmasentry_app
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Bedrock Model
BEDROCK_MODEL_ID=us.anthropic.claude-3-5-sonnet-20241022-v2:0

# Bedrock Guardrails (optional)
BEDROCK_GUARDRAIL_ID=your-guardrail-id
BEDROCK_GUARDRAIL_VERSION=DRAFT

# AgentCore Gateway (optional)
AGENTCORE_ENDPOINT=your-agentcore-endpoint

# Auth
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./pharmasentry_local.db
```

### 5. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs (Swagger UI)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🧪 Testing

### Run local agent tests

```bash
python scripts/test_local_agent.py
```

### API Health Check

```bash
curl http://localhost:8000/health
```

---

## 🤖 Agent Overview

| Agent | Description |
|-------|-------------|
| **Supervisor** | Orchestrates the multi-agent workflow, routes queries to specialized agents |
| **Label Agent** | Analyzes FDA drug labels, extracts dosage, contraindications, side effects |
| **Safety Agent** | Monitors drug-drug interactions and flags safety concerns |
| **Trials Agent** | Searches and summarizes relevant clinical trials from public databases |

---

## 🔒 Security

- All PII is automatically redacted before being sent to AI models
- Amazon Bedrock Guardrails enforce content safety policies
- JWT-based OAuth2 authentication secures all API endpoints
- Sensitive credentials are managed via environment variables (never committed)

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework & REST API |
| `strands-agents` | AWS Strands multi-agent framework |
| `boto3` | AWS SDK for Python |
| `sqlalchemy` | ORM & database management |
| `pydantic` | Data validation & serialization |
| `python-jose` | JWT token handling |
| `passlib` | Password hashing |
| `uvicorn` | ASGI server |

---

## 📄 License

This project is part of the **Generative AI Strands Learning** series. See the root repository for license details.

---

## 🙋 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request
