"""
Guardrails for agent responses - safety checks, PII redaction, and citation handling.
"""
from __future__ import annotations

import re
from app.schemas import AgentAnswer


def refuse_if_clinical_request(user_message: str) -> AgentAnswer | None:
    """
    Refuse requests that ask for clinical advice or diagnosis.
    Returns an AgentAnswer if request should be refused, None otherwise.
    """
    clinical_keywords = [
        "diagnose", "diagnosis", "treatment", "prescription", "medication",
        "should i take", "can i take", "am i", "is it safe", "will it help"
    ]
    
    message_lower = user_message.lower()
    
    for keyword in clinical_keywords:
        if keyword in message_lower:
            return AgentAnswer(
                text="I cannot provide clinical advice or diagnosis. Please consult with a healthcare professional for medical guidance.",
                citations=[],
                agent_used="SafetyGuard"
            )
    
    return None


def redact_pii(text: str) -> str:
    """
    Regex-based PII redaction for common patterns.
    Redacts: SSN, phone numbers, email addresses, credit card numbers.
    """
    # SSN pattern (XXX-XX-XXXX)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    # Phone number pattern (XXX-XXX-XXXX or (XXX) XXX-XXXX)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\(\d{3}\)\s*\d{3}[-.]?\d{4}', '[PHONE]', text)
    
    # Email pattern
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Credit card pattern (16 digits)
    text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CREDIT_CARD]', text)
    
    return text


def inject_signal_caveat(response_text: str) -> str:
    """
    Injects a caveat about pharmacovigilance signals in responses mentioning signals.
    """
    if "signal" in response_text.lower():
        caveat = "\n\n**Note:** This response discusses potential pharmacovigilance signals. Please refer to the full regulatory guidance for comprehensive information."
        return response_text + caveat
    
    return response_text


def enforce_citation_or_silence(response: AgentAnswer) -> AgentAnswer:
    """
    Ensures responses either have citations or are appropriately qualified.
    """
    if not response.citations:
        # Add disclaimer if no citations are available
        if response.text and not response.text.endswith("[No sources available for this response]"):
            response.text += "\n\n*Note: This response is based on general knowledge without specific source citations.*"
    
    return response
