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
# INTERVIEW OPERATIONS
# =============================================================================

# Language code to full name mapping
LANGUAGE_CODE_TO_NAME = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "it": "Italian",
    "ru": "Russian",
    "ar": "Arabic",
}


def get_language_name(code: str) -> str:
    """Convert language code to full name."""
    return LANGUAGE_CODE_TO_NAME.get(code, code.capitalize())


async def get_interview_by_id(interview_id: str) -> Optional[dict]:
    """
    Get interview by ID.
    
    Args:
        interview_id: The interview UUID
        
    Returns:
        Interview data dict with fields:
        - id, name, email, language, status, user_id, created_at
        - language_name: Full language name (e.g., "Spanish" instead of "es")
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available")
        return None
    
    try:
        response = client.table("interviews").select("*").eq(
            "id", interview_id
        ).single().execute()
        
        if response.data:
            # Add full language name
            data = response.data
            language_code = data.get("language", "en")
            data["language_name"] = get_language_name(language_code)
            return data
        return None
    except Exception as e:
        print(f"Error getting interview by ID: {e}")
        return None


async def update_interview_status(interview_id: str, status: str) -> Optional[dict]:
    """
    Update interview status.
    
    Args:
        interview_id: The interview UUID
        status: New status (e.g., "in_progress", "completed", "Email sent")
        
    Returns:
        Updated interview data or None
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available")
        return None
    
    try:
        response = client.table("interviews").update({
            "status": status
        }).eq("id", interview_id).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating interview status: {e}")
        return None


async def insert_interview(data: dict) -> Optional[dict]:
    """
    Insert new interview record.
    
    Args:
        data: Interview data (name, email, language, user_id)
        
    Returns:
        Created interview data or None
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available")
        return None
    
    try:
        response = client.table("interviews").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error inserting interview: {e}")
        return None


async def update_interview_evaluation(interview_id: str, evaluation: dict) -> Optional[dict]:
    """
    Store evaluation data for a completed interview.
    
    Args:
        interview_id: The interview UUID
        evaluation: Evaluation data dict containing:
            - overall_score: Percentage score (0-100)
            - grammar_score: Grammar proficiency (0-10)
            - fluency_score: Fluency proficiency (0-10)
            - proficiency_level: CEFR level (A1-C2)
            - reading_level: Reading proficiency level
            - feedback: Summary feedback text
            - total_exercises: Number of exercises completed
            
    Returns:
        Updated interview data or None
    """
    client = get_supabase()
    if not client:
        print("Supabase client not available, skipping evaluation storage")
        return None
    
    try:
        from datetime import datetime
        
        # Add timestamp to evaluation
        evaluation_with_timestamp = {
            **evaluation,
            "evaluated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        response = client.table("interviews").update({
            "evaluation": evaluation_with_timestamp,
            "status": "completed"
        }).eq("id", interview_id).execute()
        
        if response.data:
            print(f"✅ Evaluation saved for interview {interview_id}")
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error storing interview evaluation: {e}")
        return None
