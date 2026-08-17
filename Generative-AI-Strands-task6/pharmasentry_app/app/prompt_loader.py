"""
Prompt loader — loads agent system prompts from the prompts/ directory
inside the app package.
"""
from __future__ import annotations

from pathlib import Path

# prompts/ lives alongside this file inside the app/ package
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from app/prompts/<prompt_name>.txt.

    Falls back to a sensible default if the file doesn't exist so the app
    never crashes at import time just because a prompt file is missing.

    Args:
        prompt_name: Stem of the prompt file (without .txt extension).

    Returns:
        The prompt text, stripped of leading/trailing whitespace.
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}.txt"

    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()

    return _default_prompt(prompt_name)


def _default_prompt(prompt_name: str) -> str:
    """Return a built-in fallback prompt when the file is absent."""
    defaults: dict[str, str] = {
        "supervisor": (
            "You are PharmaSentry's supervisor agent. Route drug-safety and "
            "clinical-information questions to the correct specialist tool "
            "(label_agent_tool, safety_agent_tool, trials_agent_tool) and "
            "synthesise their answers into a concise, cited response. "
            "Refuse requests for clinical diagnosis or personalised treatment advice. "
            "Escalate to escalate_to_human when a question is outside your scope."
        ),
        "label_agent": (
            "You are a drug-label specialist. Answer questions about FDA-approved "
            "indications, contraindications, warnings, dosing, and interactions "
            "using the label corpus and openFDA label API. Always cite the label "
            "section and set_id."
        ),
        "safety_agent": (
            "You are a pharmacovigilance safety specialist. Report adverse-event "
            "frequencies from FAERS (openFDA drug/event). Always clarify that "
            "counts are raw reports, not causality judgements, and add the "
            "signal caveat required by regulation."
        ),
        "trials_agent": (
            "You are a clinical-trials information specialist. Search "
            "ClinicalTrials.gov v2 and summarise relevant studies with their "
            "NCT IDs, status, phase, and a link."
        ),
    }
    return defaults.get(
        prompt_name,
        "You are a helpful pharmaceutical information assistant.",
    )
