from passlib.context import CryptContext
import uuid
from fastapi import Header
from typing import Optional

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash(password: str) -> str:
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_correlation_id(x_correlation_id: Optional[str] = Header(None)) -> str:
    """
    Get or generate a correlation ID for tracking requests.
    """
    return x_correlation_id or str(uuid.uuid4())