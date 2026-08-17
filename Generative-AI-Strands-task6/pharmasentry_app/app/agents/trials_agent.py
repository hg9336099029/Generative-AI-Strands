"""
TrialsAgent — specialist for clinical trial discovery.

Exposes a Strands @tool function `trials_agent_tool` so the Supervisor can
call it as part of the "agents-as-tools" pattern.  Internally it runs its
own Strands Agent equipped with:
  - clinicaltrials_search : ClinicalTrials.gov API v2 search
"""
from __future__ import annotations

from strands import Agent, tool

from app.agents.model_provider import get_model
from app.prompt_loader import load_prompt
from app.tools.trials import clinicaltrials_search

TRIALS_AGENT_SYSTEM_PROMPT = load_prompt("trials_agent")

# Module-level singleton
_trials_agent: Agent | None = None


def _get_trials_agent() -> Agent:
    global _trials_agent
    if _trials_agent is None:
        _trials_agent = Agent(
            model=get_model(),
            system_prompt=TRIALS_AGENT_SYSTEM_PROMPT,
            tools=[clinicaltrials_search],
            callback_handler=None,
        )
    return _trials_agent


@tool
def trials_agent_tool(query: str) -> str:
    """
    Clinical-trials specialist. Searches ClinicalTrials.gov v2 for studies
    relevant to a drug, condition, or research question and summarises the
    most pertinent results with study links.

    Only call this for questions about clinical trials — not for label text
    (use label_agent_tool) or adverse events (use safety_agent_tool).

    Args:
        query: The user's question about clinical trials or research evidence.

    Returns:
        Summary of relevant clinical trials with NCT IDs and links.
    """
    try:
        agent = _get_trials_agent()
        response = agent(query)
        return str(response)
    except Exception as exc:
        return f"TrialsAgent error: {exc}"