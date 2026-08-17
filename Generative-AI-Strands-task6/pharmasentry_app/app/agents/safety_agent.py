"""
SafetyAgent — specialist for adverse-event frequency and safety signals.

Exposes a Strands @tool function `safety_agent_tool` so the Supervisor can
call it as part of the "agents-as-tools" pattern.  Internally it runs its
own Strands Agent equipped with:
  - openfda_event_counts : raw FAERS adverse-event counts (also exposed via
                           AgentCore Gateway as an MCP target — see
                           gateway_target.py — so the same underlying data
                           is reachable either in-process or via MCP)
"""
from __future__ import annotations

from strands import Agent, tool

from app.agents.model_provider import get_model
from app.prompt_loader import load_prompt
from app.tools.openfda import openfda_event_counts

SAFETY_AGENT_SYSTEM_PROMPT = load_prompt("safety_agent")

# Module-level singleton
_safety_agent: Agent | None = None


def _get_safety_agent() -> Agent:
    global _safety_agent
    if _safety_agent is None:
        _safety_agent = Agent(
            model=get_model(),
            system_prompt=SAFETY_AGENT_SYSTEM_PROMPT,
            tools=[openfda_event_counts],
            callback_handler=None,
        )
    return _safety_agent


@tool
def safety_agent_tool(query: str) -> str:
    """
    Pharmacovigilance safety specialist. Answers questions about adverse-event
    frequencies and safety signals using FAERS data from the openFDA API.

    Always qualifies results as raw report counts (no causality, no rate
    normalisation) and adds the required signal caveat.

    Only call this for questions about adverse events, side effects, or safety
    signals — not for label text (use label_agent_tool) or clinical trials
    (use trials_agent_tool).

    Args:
        query: The user's question about adverse events or safety signals.

    Returns:
        Answer with FAERS data, counts, and signal caveats.
    """
    try:
        agent = _get_safety_agent()
        response = agent(query)
        return str(response)
    except Exception as exc:
        return f"SafetyAgent error: {exc}"