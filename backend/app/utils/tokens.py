"""Token utilities."""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple


def generate_token(length: int = 32) -> str:
    """Generate a URL-safe token."""
    return secrets.token_urlsafe(length)


def generate_interview_token() -> str:
    """Generate a unique interview access token."""
    return generate_token(32)


def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_expiring_token(hours: int = 72) -> Tuple[str, datetime]:
    """Create a token with expiration time."""
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=hours)
    return token, expires_at


def is_expired(expires_at: datetime) -> bool:
    """Check if a timestamp is in the past."""
    return datetime.utcnow() > expires_at


def parse_token(token: str) -> Optional[dict]:
    """
    Parse and validate a token.
    
    TODO: Implement token parsing/validation
    """
    if not token or len(token) < 10:
        return None
    return {"token": token, "valid": True}
