from supabase import create_client, Client
from app.core.config import settings

# Initialize Supabase client
# TODO: Handle missing credentials gracefully
supabase: Client | None = None

if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase() -> Client | None:
    """Get Supabase client instance."""
    return supabase


# TODO: Add helper functions for common operations
# def insert_interview(data: dict) -> dict:
#     pass

# def get_interview_by_id(interview_id: str) -> dict:
#     pass

# def update_interview_status(interview_id: str, status: str) -> dict:
#     pass
