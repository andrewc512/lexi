"""
Session API endpoints for language proficiency assessment.

These endpoints handle the language assessment flow:
- Starting a new assessment
- Processing exercises (speaking + translation)
- Managing session state
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional

from app.models.session import AssessmentTurnResponse, SessionState
from app.services.agent import assessment_agent
from app.services import supabase

router = APIRouter()


@router.post("/start/{assessment_id}")
async def start_assessment(
    assessment_id: str,
    target_language: str = Form(...)
) -> AssessmentTurnResponse:
    """
    Start a new language assessment session.

    Args:
        assessment_id: Unique assessment identifier
        target_language: Language being assessed (e.g., "Spanish", "French")

    Flow:
        1. Initialize session state
        2. Agent generates first speaking prompt
        3. Store session state in database
        4. Return first exercise to frontend

    Returns:
        Initial prompt + session state
    """

    # TODO: Verify assessment doesn't already exist
    # existing_session = await supabase.get_session_state(assessment_id)
    # if existing_session:
    #     raise HTTPException(status_code=400, detail="Assessment already started")

    # Start assessment with agent
    try:
        initial_response, session_state = await assessment_agent.start_assessment(
            assessment_id=assessment_id,
            target_language=target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

    # TODO: Store session state in database
    # await supabase.create_session_state(session_state)

    return AssessmentTurnResponse(
        agent_response=initial_response,
        session_state=session_state,
        exercises_completed=0,
        current_phase=session_state.current_phase
    )


@router.post("/exercise/{assessment_id}")
async def submit_exercise(
    assessment_id: str,
    audio: Optional[UploadFile] = File(None),
    translation_text: Optional[str] = Form(None)
) -> AssessmentTurnResponse:
    """
    Submit an exercise response (speaking or translation).

    Args:
        assessment_id: Unique assessment identifier
        audio: Audio file (for speaking exercises or spoken translations)
        translation_text: Text translation (alternative to audio for translation exercises)

    Flow:
        1. Load current session state from database
        2. Read audio bytes or text
        3. Agent evaluates response and generates next exercise
        4. Store updated state in database
        5. Return evaluation + next exercise

    Returns:
        Evaluation of current exercise + next exercise prompt
    """

    if not audio and not translation_text:
        raise HTTPException(
            status_code=400,
            detail="Must provide either audio file or translation text"
        )

    # TODO: Load session state from database
    # session_state = await supabase.get_session_state(assessment_id)
    # if not session_state:
    #     raise HTTPException(status_code=404, detail="Assessment not found. Start assessment first.")

    # STUB: For now, create mock session state
    # Replace with actual database load
    session_state = SessionState(
        assessment_id=assessment_id,
        target_language="Spanish",  # TODO: Load from DB
        current_phase="speaking_test",
        current_difficulty=2
    )

    # Read audio if provided
    audio_bytes = None
    if audio:
        audio_bytes = await audio.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

    # Process exercise with agent
    try:
        response, updated_state = await assessment_agent.process_exercise(
            session_state=session_state,
            audio_bytes=audio_bytes,
            text_response=translation_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process exercise: {str(e)}")

    # TODO: Store updated state in database
    # await supabase.update_session_state(assessment_id, updated_state)

    # TODO: If assessment concluded, store final evaluation
    # if not response.should_continue:
    #     proficiency = await llm.calculate_overall_proficiency(updated_state)
    #     await supabase.store_final_evaluation(assessment_id, proficiency)

    return AssessmentTurnResponse(
        agent_response=response,
        session_state=updated_state,
        exercises_completed=len(updated_state.exercises_completed),
        current_phase=updated_state.current_phase
    )


@router.get("/state/{assessment_id}")
async def get_assessment_state(assessment_id: str) -> SessionState:
    """
    Get current assessment state.

    Useful for:
    - Resuming interrupted assessments
    - Debugging exercise flow
    - Frontend state synchronization
    """

    # TODO: Load from database
    # session_state = await supabase.get_session_state(assessment_id)
    # if not session_state:
    #     raise HTTPException(status_code=404, detail="Assessment not found")
    # return session_state

    # STUB: Return mock state
    return SessionState(
        assessment_id=assessment_id,
        target_language="Spanish",
        current_phase="speaking_test",
        current_difficulty=3
    )


@router.get("/results/{assessment_id}")
async def get_results(assessment_id: str):
    """
    Get final assessment results.

    Returns:
    - CEFR proficiency level
    - Grammar/fluency scores
    - Detailed feedback per exercise
    """

    # TODO: Load from database
    # session_state = await supabase.get_session_state(assessment_id)
    # if not session_state:
    #     raise HTTPException(status_code=404, detail="Assessment not found")

    # if session_state.current_phase != "complete":
    #     raise HTTPException(status_code=400, detail="Assessment not yet completed")

    # proficiency = await llm.calculate_overall_proficiency(session_state)

    # STUB: Return mock results
    return {
        "assessment_id": assessment_id,
        "target_language": "Spanish",
        "proficiency_level": "B1",
        "overall_grammar_score": 78.5,
        "overall_fluency_score": 72.0,
        "exercises_completed": 10,
        "feedback": "Good intermediate proficiency. Continue practicing verb conjugations.",
        "strengths": [
            "Natural conversational flow",
            "Good vocabulary range",
            "Accurate translations of common phrases"
        ],
        "areas_for_improvement": [
            "Subjunctive mood usage",
            "Complex sentence structures",
            "Idiomatic expressions"
        ]
    }


@router.delete("/state/{assessment_id}")
async def end_assessment(assessment_id: str):
    """
    Explicitly end an assessment session.

    This should:
    - Mark assessment as completed
    - Calculate final proficiency
    - Archive session state
    """

    # TODO: Load and finalize assessment
    # session_state = await supabase.get_session_state(assessment_id)
    # proficiency = await llm.calculate_overall_proficiency(session_state)
    # await supabase.store_final_evaluation(assessment_id, proficiency)
    # await supabase.update_assessment_status(assessment_id, "completed")

    return {
        "message": "Assessment ended successfully",
        "assessment_id": assessment_id
    }
