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


# =============================================================================
# SESSION STATE CRUD OPERATIONS
# =============================================================================

async def create_session_state(session_state: "SessionState") -> dict:
    """
    Create a new assessment session state in the database.

    TODO: Implement with Supabase
    Example:
        response = supabase.table("session_states").insert({
            "assessment_id": session_state.assessment_id,
            "target_language": session_state.target_language,
            "current_phase": session_state.current_phase,
            "current_difficulty": session_state.current_difficulty,
            "exercises_completed": [e.model_dump() for e in session_state.exercises_completed],
            "speaking_exercises_done": session_state.speaking_exercises_done,
            "translation_exercises_done": session_state.translation_exercises_done,
            "insights": session_state.insights,
            "started_at": session_state.started_at,
            "last_updated": session_state.last_updated
        }).execute()

        return response.data[0]
    """
    pass


async def get_session_state(assessment_id: str) -> "SessionState":
    """
    Retrieve session state from database.

    TODO: Implement with Supabase
    Example:
        from app.models.session import SessionState, LanguageExercise

        response = supabase.table("session_states").select("*").eq(
            "assessment_id", assessment_id
        ).execute()

        if not response.data:
            return None

        data = response.data[0]

        # Convert exercises back to LanguageExercise objects
        exercises = [LanguageExercise(**e) for e in data["exercises_completed"]]

        return SessionState(
            assessment_id=data["assessment_id"],
            target_language=data["target_language"],
            current_phase=data["current_phase"],
            current_difficulty=data["current_difficulty"],
            exercises_completed=exercises,
            speaking_exercises_done=data["speaking_exercises_done"],
            translation_exercises_done=data["translation_exercises_done"],
            insights=data["insights"],
            started_at=data["started_at"],
            last_updated=data["last_updated"]
        )
    """
    pass


async def update_session_state(assessment_id: str, session_state: "SessionState") -> dict:
    """
    Update existing session state in database.

    TODO: Implement with Supabase
    Example:
        response = supabase.table("session_states").update({
            "current_phase": session_state.current_phase,
            "current_difficulty": session_state.current_difficulty,
            "exercises_completed": [e.model_dump() for e in session_state.exercises_completed],
            "speaking_exercises_done": session_state.speaking_exercises_done,
            "translation_exercises_done": session_state.translation_exercises_done,
            "insights": session_state.insights,
            "last_updated": session_state.last_updated,
            "overall_grammar_score": session_state.overall_grammar_score,
            "overall_fluency_score": session_state.overall_fluency_score,
            "overall_proficiency_level": session_state.overall_proficiency_level
        }).eq("assessment_id", assessment_id).execute()

        return response.data[0]
    """
    pass


# =============================================================================
# LEGACY INTERVIEW OPERATIONS (Keep for backwards compatibility)
# =============================================================================

async def insert_interview(data: dict) -> dict:
    """Insert new interview record."""
    pass


async def get_interview_by_id(interview_id: str) -> dict:
    """Get interview by ID."""
    pass


async def update_interview_status(interview_id: str, status: str) -> dict:
    """Update interview status."""
    pass
