"""
Supervisor Agent — routes user queries to the three specialist agents.

Uses the "agents-as-tools" pattern: each specialist is exposed as a @tool
function that the Supervisor's Strands Agent can call like any other tool.

Memory integration:
  - STM: last-K turns from the session are prepended to the system prompt so
    the Supervisor has conversational context.
  - LTM: the user's scoped product of interest (e.g. "lisinopril") is read
    from long-term memory and also injected into the prompt so the user doesn't
    have to repeat it every session.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from strands import Agent

from app.agents.guardrails import (
    enforce_citation_or_silence,
    inject_signal_caveat,
    refuse_if_clinical_request,
)
from app.agents.label_agent import label_agent_tool
from app.agents.model_provider import get_model
from app.agents.safety_agent import safety_agent_tool
from app.agents.trials_agent import trials_agent_tool
from app.prompt_loader import load_prompt
from app.schemas import AgentAnswer, Citation
from app.tools.escalate import escalate_to_human

SUPERVISOR_SYSTEM_PROMPT = load_prompt("supervisor")

# Module-level singleton supervisor agent
_supervisor_agent: Agent | None = None


def _get_supervisor(memory_context: str = "") -> Agent:
    """
    Return a Supervisor Agent.  If memory context is provided a fresh agent
    with the enriched system prompt is created (context changes per request).
    The base agent is cached for when there is no context.
    """
    global _supervisor_agent

    if memory_context:
        # Inject memory context into a request-scoped agent
        enriched_prompt = (
            f"{SUPERVISOR_SYSTEM_PROMPT}\n\n"
            f"--- Memory context ---\n{memory_context}\n--- End of context ---"
        )
        return Agent(
            model=get_model(),
            system_prompt=enriched_prompt,
            tools=[label_agent_tool, safety_agent_tool, trials_agent_tool, escalate_to_human],
            callback_handler=None,  # suppress default stdout printer
        )

    if _supervisor_agent is None:
        _supervisor_agent = Agent(
            model=get_model(),
            system_prompt=SUPERVISOR_SYSTEM_PROMPT,
            tools=[label_agent_tool, safety_agent_tool, trials_agent_tool, escalate_to_human],
            callback_handler=None,  # suppress default stdout printer
        )
    return _supervisor_agent



def run_supervisor(
    user_message: str,
    memory_context: str = "",
) -> AgentAnswer:
    """
    Synchronous convenience wrapper used by the agent_client
    (called via asyncio.to_thread to avoid blocking the event loop).

    Args:
        user_message: The user's input message.
        memory_context: Pre-formatted string with STM turns + LTM facts.

    Returns:
        AgentAnswer with response text and citations.
    """
    # Guardrail: refuse clinical advice requests before touching any agent
    refusal = refuse_if_clinical_request(user_message)
    if refusal:
        return refusal

    agent = _get_supervisor(memory_context=memory_context)
    raw_result = agent(user_message)
    text = str(raw_result)

    # Apply post-processing guardrails
    text = inject_signal_caveat(text)

    # Determine which specialist was used (best-effort from response text)
    agent_used = "SupervisorAgent"
    signal_present = False
    if "signal" in text.lower() or "faers" in text.lower():
        signal_present = True
        agent_used = "SafetyAgent→SupervisorAgent"
    elif "nct" in text.lower() or "clinicaltrial" in text.lower():
        agent_used = "TrialsAgent→SupervisorAgent"
    elif "label" in text.lower() or "prescribing information" in text.lower():
        agent_used = "LabelAgent→SupervisorAgent"

    answer = AgentAnswer(
        text=text,
        citations=[Citation(title="PharmaSentry", source="FDA/NIH/ClinicalTrials.gov")],
        agent_used=agent_used,
        signal_present=signal_present,
    )
    return enforce_citation_or_silence(answer)
