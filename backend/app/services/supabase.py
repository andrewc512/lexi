from typing import Optional
from app.core.config import settings
from app.models.session import SessionState, LanguageExercise

# Initialize Supabase client lazily to avoid import errors if not installed
_supabase_client = None


def get_supabase():
    """Get Supabase client instance (lazy initialization)."""
    global _supabase_client
    
    if _supabase_client is None:
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                from supabase import create_client
                _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            except ImportError:
                print("Warning: supabase package not installed. Database operations will fail.")
                return None
        else:
            print("Warning: SUPABASE_URL or SUPABASE_KEY not configured.")
            return None
    
    return _supabase_client


# =============================================================================
# SESSION STATE CRUD OPERATIONS
# =============================================================================

async def create_session_state(session_state: SessionState) -> Optional[dict]:
    """
    Create a new assessment session state in the database.
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available, skipping database write")
        return None
    
    try:
        response = client.table("session_states").insert({
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
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating session state: {e}")
        return None


async def get_session_state(assessment_id: str) -> Optional[SessionState]:
    """
    Retrieve session state from database.
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available")
        return None
    
    try:
        response = client.table("session_states").select("*").eq(
            "assessment_id", assessment_id
        ).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        
        # Convert exercises back to LanguageExercise objects
        exercises = []
        if data.get("exercises_completed"):
            exercises = [LanguageExercise(**e) for e in data["exercises_completed"]]
        
        return SessionState(
            assessment_id=data["assessment_id"],
            target_language=data["target_language"],
            current_phase=data["current_phase"],
            current_difficulty=data["current_difficulty"],
            exercises_completed=exercises,
            speaking_exercises_done=data.get("speaking_exercises_done", 0),
            translation_exercises_done=data.get("translation_exercises_done", 0),
            overall_grammar_score=data.get("overall_grammar_score"),
            overall_fluency_score=data.get("overall_fluency_score"),
            overall_proficiency_level=data.get("overall_proficiency_level"),
            insights=data.get("insights", []),
            started_at=data.get("started_at", ""),
            last_updated=data.get("last_updated", "")
        )
    except Exception as e:
        print(f"Error getting session state: {e}")
        return None


async def update_session_state(assessment_id: str, session_state: SessionState) -> Optional[dict]:
    """
    Update existing session state in database.
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available, skipping database update")
        return None
    
    try:
        response = client.table("session_states").update({
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
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating session state: {e}")
        return None


async def store_final_evaluation(assessment_id: str, proficiency: dict) -> Optional[dict]:
    """
    Store the final evaluation scores when assessment is complete.
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available, skipping evaluation storage")
        return None
    
    try:
        response = client.table("session_states").update({
            "current_phase": "complete",
            "overall_grammar_score": proficiency.get("grammar_score"),
            "overall_fluency_score": proficiency.get("fluency_score"),
            "overall_proficiency_level": proficiency.get("proficiency_level")
        }).eq("assessment_id", assessment_id).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error storing final evaluation: {e}")
        return None


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
