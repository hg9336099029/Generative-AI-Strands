import os
from pathlib import Path

# AWS SSO is used for credentials — no .env loading needed.
# Run `aws sso login` before starting the app.
BASE_DIR = Path(__file__).resolve().parent.parent


def _get_env(*keys, default=None):
    """Read from real environment variables only (no .env file)."""
    for key in keys:
        value = os.getenv(key)
        if value is not None and str(value).strip():
            return value
    return default


class Settings:
    def __init__(self):
        # ----- Database -----
        self.database_hostname = _get_env("DATABASE_HOSTNAME", default="localhost")
        self.database_password = _get_env("DATABASE_PASSWORD", default="12345678")
        self.database_port = _get_env("DATABASE_PORT", default="5432")
        self.database_name = _get_env("DATABASE_NAME", default="pharmasentry")
        self.database_username = _get_env("DATABASE_USERNAME", default="postgres")

        # ----- Auth -----
        self.secret_key = _get_env("SECRET_KEY", default="changeme-set-a-real-secret-in-env")
        self.algorithm = _get_env("ALGORITHM", default="HS256")
        expire_str = _get_env("ACCESS_TOKEN_EXPIRE_MINUTES", default="30")
        self.access_token_expire_minutes = int(expire_str) if expire_str else 30

        # ----- AWS / AgentCore -----
        # Credentials come from the boto3 default credential chain:
        #   1. AWS SSO token cache  (~/.aws/sso/cache/)
        #   2. Environment variables (CI / container)
        #   3. EC2 instance metadata
        # Run `aws sso login` before starting the app. No .env needed.
        self.aws_profile = _get_env("AWS_PROFILE", "AWS_DEFAULT_PROFILE", default="")
        self.aws_region = _get_env("AWS_REGION", default="ap-south-1")  # Mumbai
        self.agentcore_memory_id = _get_env("AGENTCORE_MEMORY_ID", default="")
        self.agentcore_gateway_id = _get_env("AGENTCORE_GATEWAY_ID", default="")

        # ----- Model -----
        # Always uses Bedrock via AWS SSO — no API key required.
        # Override MODEL_TYPE env var to switch providers if needed.
        self.model_type = _get_env("MODEL_TYPE", default="bedrock")
        self.anthropic_api_key = _get_env("ANTHROPIC_API_KEY", default="")
        # Optional: set BEDROCK_MODEL_ID env var to override the model.
        # If not set, Strands uses its own default model (no hardcoded value).
        self.bedrock_model_id = _get_env("BEDROCK_MODEL_ID", default=None)

        # ----- Local stub mode -----
        # false → real Bedrock + AgentCore Memory (AWS SSO required)
        # true  → SQLite + in-process memory (no AWS needed)
        stub_env = _get_env("PHARMASENTRY_LOCAL_STUB", default="false")
        self.local_stub = (stub_env or "false").lower() == "true"

        # ----- openFDA -----
        self.openfda_api_key = _get_env("OPENFDA_API_KEY", default="")

        # ----- Label index -----
        self.label_index_path = _get_env(
            "LABEL_INDEX_PATH", default="data/index/label_index.json"
        )


settings = Settings()