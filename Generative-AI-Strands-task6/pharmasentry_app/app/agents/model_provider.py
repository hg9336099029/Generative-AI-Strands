"""
Model provider — returns a valid Strands BedrockModel via AWS SSO.

Credential resolution order (all managed by boto3, no .env required):
  1. AWS SSO token cache  (~/.aws/sso/cache/)  ← primary for intern accounts
  2. Environment variables (AWS_ACCESS_KEY_ID etc.)  ← CI / container
  3. EC2/ECS instance metadata

Before starting the app, log in once:
    aws sso login

Region: ap-south-1 (Mumbai) by default.
Model:  apac.anthropic.claude-3-5-sonnet-20241022-v2:0  (APAC cross-region inference profile).
"""
from __future__ import annotations

from typing import Any, AsyncGenerator, AsyncIterable

from strands.models.model import Model
from strands.types.streaming import StreamEvent
from strands.types.content import Messages

# ---------------------------------------------------------------------------
# Region constant — single source of truth, no .env required
# ---------------------------------------------------------------------------
AWS_REGION = "ap-south-1"



def _make_boto3_session():
    """
    Build a boto3 Session using the default credential chain.

    boto3 resolves credentials automatically in this order:
      1. SSO token cache  (~/.aws/sso/cache/<hash>.json)  ← AWS SSO
      2. Environment variables (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY)
      3. EC2 / ECS instance metadata

    No explicit access_key / secret_key / profile is passed here — SSO manages
    everything after `aws sso login`.
    """
    import boto3
    print(f"[model_provider] Using default AWS credential chain / region: {AWS_REGION}")
    return boto3.Session(region_name=AWS_REGION)


def get_model() -> Model:
    """
    Return a Strands BedrockModel using AWS SSO credentials.

    The boto3 session is built from the default credential chain — no .env
    or hard-coded keys are required.  Just run `aws sso login` once.

    Region: ap-south-1 (Mumbai)
    Model:  anthropic.claude-3-5-sonnet-20241022-v2:0 (default AgentCore LLM)
    """
    from app.config import settings

    try:
        import boto3
        from strands.models import BedrockModel  # type: ignore[import]

        session = _make_boto3_session()

        # Validate SSO session is active — gives a clear error instead of
        # a cryptic Bedrock 403 if the token has expired.
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(
            f"[model_provider] AWS SSO authenticated as: "
            f"{identity.get('Arn', 'unknown')}"
        )

        # BedrockModel accepts a boto3 session directly (Strands >=1.0).
        # Only pass model_id when explicitly set via BEDROCK_MODEL_ID env var;
        # otherwise Strands uses its own built-in default.
        bedrock_kwargs: dict = {"boto_session": session}
        if settings.bedrock_model_id:
            bedrock_kwargs["model_id"] = settings.bedrock_model_id
            print(f"[model_provider] Using model: {settings.bedrock_model_id}")
        else:
            print("[model_provider] No BEDROCK_MODEL_ID set — using Strands default model")
        return BedrockModel(**bedrock_kwargs)

    except Exception as exc:
        print(
            f"[model_provider] BedrockModel/SSO unavailable: {exc}\n"
            "  Make sure you ran: aws sso login"
        )
        return _StrandsStubModel()


# ---------------------------------------------------------------------------
# Stub model — implements the full Strands Model ABC
# ---------------------------------------------------------------------------

_STUB_TEXT = (
    "[STUB MODE] PharmaSentry is running without a real LLM. "
    "Set MODEL_TYPE=bedrock (with AWS credentials) or MODEL_TYPE=anthropic "
    "(with ANTHROPIC_API_KEY) in your .env to enable real agent responses. "
    "The routing pipeline, memory, and tools are all fully wired."
)


class _StrandsStubModel(Model):
    """
    Concrete implementation of the Strands Model ABC that returns a canned
    response.  Lets the full pipeline (event loop, tool routing, memory) run
    locally without touching any cloud service.
    """

    # --- Model.get_config / update_config ---

    def get_config(self) -> dict[str, Any]:
        return {
            "model_id": "stub-model",
            "context_window_limit": 8192,
            "max_tokens": 1024,
        }

    def update_config(self, **model_config: Any) -> None:
        pass  # No-op for stub

    # --- Model.stream (the main entry point Strands calls) ---

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[Any] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: Any | None = None,
        system_prompt_content: list[Any] | None = None,
        invocation_state: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        """
        Async generator that yields a minimal but spec-compliant sequence of
        StreamEvents. Strands' event loop iterates this with 'async for'.
        """
        # 1. messageStart
        yield {"messageStart": {"role": "assistant"}}  # type: ignore[misc]

        # 2. contentBlockStart
        yield {"contentBlockStart": {"start": {"text": ""}, "contentBlockIndex": 0}}  # type: ignore[misc]

        # 3. contentBlockDelta — the actual text
        yield {  # type: ignore[misc]
            "contentBlockDelta": {
                "delta": {"text": _STUB_TEXT},
                "contentBlockIndex": 0,
            }
        }

        # 4. contentBlockStop
        yield {"contentBlockStop": {"contentBlockIndex": 0}}  # type: ignore[misc]

        # 5. messageStop
        yield {"messageStop": {"stopReason": "end_turn"}}  # type: ignore[misc]

        # 6. metadata
        yield {  # type: ignore[misc]
            "metadata": {
                "usage": {
                    "inputTokens": 10,
                    "outputTokens": len(_STUB_TEXT) // 4,
                    "totalTokens": 10 + len(_STUB_TEXT) // 4,
                },
                "metrics": {"latencyMs": 0},
            }
        }

    async def structured_output(
        self,
        output_model: type,
        prompt: Messages,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Return a stub structured output (empty instance of the output model)."""
        try:
            obj = output_model.model_construct()
        except Exception:
            obj = {}
        yield {"output": obj}

