"""
LabelAgent — specialist for approved drug-label information.

Exposes a Strands @tool function `label_agent_tool` so the Supervisor can
call it as part of the "agents-as-tools" pattern.  Internally it runs its
own Strands Agent equipped with:
  - label_corpus_search  : BM25 retrieval over the curated label corpus
  - openfda_label_search : live FDA label API for cross-checking
"""
from __future__ import annotations

from strands import Agent, tool

from app.agents.model_provider import get_model
from app.prompt_loader import load_prompt
from app.tools.label_search import label_corpus_search
from app.tools.openfda import openfda_label_search

LABEL_AGENT_SYSTEM_PROMPT = load_prompt("label_agent")

# Module-level singleton — avoids rebuilding the agent on every call
_label_agent: Agent | None = None


def _get_label_agent() -> Agent:
    global _label_agent
    if _label_agent is None:
        _label_agent = Agent(
            model=get_model(),
            system_prompt=LABEL_AGENT_SYSTEM_PROMPT,
            tools=[label_corpus_search, openfda_label_search],
            callback_handler=None,
        )
    return _label_agent


@tool
def label_agent_tool(query: str) -> str:
    """
    Drug-label specialist. Answers questions about FDA-approved indications,
    contraindications, warnings, boxed warnings, dosing, and drug interactions
    using the approved label corpus and the live openFDA label API.

    Only call this for questions about what a drug label says — not for
    adverse-event frequencies (use safety_agent_tool) or clinical trials
    (use trials_agent_tool).

    Args:
        query: The user's question about a drug label.

    Returns:
        Answer with citations from the approved label.
    """
    try:
        agent = _get_label_agent()
        response = agent(query)
        return str(response)
    except Exception as exc:
        return f"LabelAgent error: {exc}"