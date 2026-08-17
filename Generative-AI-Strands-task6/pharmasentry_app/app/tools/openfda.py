"""
openFDA tools, used directly by LabelAgent (label endpoint) and SafetyAgent
(event endpoint). The event-count tool is also the one we expose through
AgentCore Gateway as an MCP target (see agent/gateway_target.py) instead of
calling it in-process, per the capstone's Gateway requirement -- SafetyAgent
calls the *same* underlying function either way; only the transport differs.
"""
from __future__ import annotations
import os
from typing import Any
import httpx
from strands import tool

OPENFDA_BASE_URL = os.environ.get("OPENFDA_BASE_URL", "https://api.fda.gov")


@tool
def openfda_label_search(product_name: str, section: str = "warnings") -> dict[str, Any]:
    """
    Look up an approved drug label section from openFDA's drug/label endpoint.

    Args:
        product_name: Brand or generic name, e.g. "lisinopril".
        section: Label section to return. One of: warnings, adverse_reactions,
            dosage_and_administration, contraindications, indications_and_usage,
            drug_interactions, boxed_warning.

    Returns:
        dict with keys: found (bool), set_id, product_name, section, text,
        source_url. `text` is the raw label text for the requested section --
        the caller (LabelAgent) is responsible for citing it, never restating
        it as independent fact.
    """
    params = {"search": f'openfda.generic_name:"{product_name}"', "limit": 1}
    try:
        resp = httpx.get(f"{OPENFDA_BASE_URL}/drug/label.json", params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"found": False, "error": str(e)}

    results = data.get("results", [])
    if not results:
        return {"found": False, "product_name": product_name}

    record = results[0]
    set_id = record.get("set_id", "unknown")
    text_field = record.get(section)
    text = text_field[0] if isinstance(text_field, list) and text_field else None

    return {
        "found": text is not None,
        "set_id": set_id,
        "product_name": product_name,
        "section": section,
        "text": text,
        "source_url": f"https://labels.fda.gov/{set_id}" if text else None,
    }


@tool
def openfda_event_counts(product_name: str, event_term: str | None = None, limit: int = 10) -> dict[str, Any]:
    """
    Query openFDA's drug/event (FAERS) endpoint for adverse-event report
    counts for a product, optionally filtered/grouped by a specific event
    term. This returns RAW REPORT COUNTS ONLY -- no causality, no rate
    normalization. SafetyAgent's stats tool turns these into a
    disproportionality signal (PRR) with the required caveat.

    Args:
        product_name: Generic drug name, e.g. "metformin".
        event_term: Optional MedDRA-ish reaction term to filter to, e.g. "nausea".
        limit: Max number of grouped results to return (1-50).

    Returns:
        dict with keys: found, product_name, total_reports, top_events
        (list of {term, count}), source_url.
    """
    search = f'patient.drug.medicinalproduct:"{product_name}"'
    if event_term:
        search += f' AND patient.reaction.reactionmeddrapt:"{event_term}"'

    params = {
        "search": search,
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": str(max(1, min(limit, 50))),
    }
    try:
        resp = httpx.get(f"{OPENFDA_BASE_URL}/drug/event.json", params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"found": False, "error": str(e)}

    results = data.get("results", [])
    if not results:
        return {"found": False, "product_name": product_name}

    top_events = [{"term": r["term"], "count": r["count"]} for r in results]
    total_reports = sum(r["count"] for r in results)

    return {
        "found": True,
        "product_name": product_name,
        "total_reports": total_reports,
        "top_events": top_events,
        "source_url": f"{OPENFDA_BASE_URL}/drug/event.json?search={search}",
    }