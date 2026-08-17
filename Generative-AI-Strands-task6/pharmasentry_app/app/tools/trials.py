"""ClinicalTrials.gov API v2 search tool, used by TrialsAgent only."""
from __future__ import annotations

import os
from typing import Any

import httpx
from strands import tool

CTGOV_BASE_URL = os.environ.get("CTGOV_BASE_URL", "https://clinicaltrials.gov/api/v2")


@tool
def clinicaltrials_search(
    condition_or_product: str,
    status: str = "RECRUITING",
    max_results: int = 5,
) -> dict[str, Any]:
    """
    Search ClinicalTrials.gov v2 for studies matching a drug/product name or
    condition.

    Args:
        condition_or_product: Free-text query, e.g. "sertraline" or
            "treatment-resistant depression".
        status: Overall status filter, e.g. RECRUITING, COMPLETED,
            ACTIVE_NOT_RECRUITING, ALL.
        max_results: 1-20.

    Returns:
        dict with keys: found, query, studies (list of {nct_id, title,
        status, phase, url}).
    """
    params = {
        "query.term": condition_or_product,
        "pageSize": str(max(1, min(max_results, 20))),
    }
    if status and status.upper() != "ALL":
        params["filter.overallStatus"] = status.upper()

    try:
        resp = httpx.get(f"{CTGOV_BASE_URL}/studies", params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as e:
        return {"found": False, "error": str(e)}

    studies_raw = data.get("studies", [])
    if not studies_raw:
        return {"found": False, "query": condition_or_product}

    studies = []
    for s in studies_raw:
        protocol = s.get("protocolSection", {})
        ident = protocol.get("identificationModule", {})
        status_mod = protocol.get("statusModule", {})
        design = protocol.get("designModule", {})
        nct_id = ident.get("nctId", "unknown")
        studies.append(
            {
                "nct_id": nct_id,
                "title": ident.get("briefTitle", ""),
                "status": status_mod.get("overallStatus", ""),
                "phase": (design.get("phases") or ["N/A"])[0],
                "url": f"https://clinicaltrials.gov/study/{nct_id}",
            }
        )

    return {"found": True, "query": condition_or_product, "studies": studies}