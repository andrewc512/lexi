import secrets
from datetime import datetime, timedelta

# TODO: Implement proper token validation if needed


def generate_interview_token() -> str:
    """Generate a unique token for interview access."""
    return secrets.token_urlsafe(32)


def validate_token(token: str) -> bool:
    """Validate an interview token."""
    # TODO: Check token against database
    # TODO: Check expiration
    return len(token) > 0


def is_token_expired(created_at: datetime, expiry_hours: int = 72) -> bool:
    """Check if a token has expired."""
    expiry_time = created_at + timedelta(hours=expiry_hours)
    return datetime.utcnow() > expiry_time
