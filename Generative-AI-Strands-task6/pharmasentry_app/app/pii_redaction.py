"""
PII redaction for adverse-event narratives. Presidio is the real engine
(NER-based, catches names/locations/etc. that regex misses); the regex
fallback in agent/guardrails.py::redact_pii covers the case where Presidio's
model download isn't available (e.g. offline dev) so the pipeline still
degrades safely instead of throwing.

This runs BEFORE the narrative touches a log line, an OTel span attribute,
or the DB's narrative_redacted column -- never on the raw narrative.
"""
from __future__ import annotations

from app.agents.guardrails import redact_pii as _regex_redact

_analyzer = None
_anonymizer = None


def _get_presidio():
    global _analyzer, _anonymizer
    if _analyzer is None:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine

        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


def redact_narrative(text: str) -> str:
    """
    Best-effort NER-based redaction via Presidio, falling back to the
    lightweight regex pass if Presidio's spaCy model isn't installed in
    this environment. Always returns a redacted string, never raises.
    """
    try:
        analyzer, anonymizer = _get_presidio()
        results = analyzer.analyze(
            text=text,
            entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", "DATE_TIME", "US_SSN"],
            language="en",
        )
        anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
        return anonymized.text
    except Exception:
        # Offline dev / spaCy model not downloaded -- degrade to regex pass
        # rather than failing the whole intake request.
        return _regex_redact(text)