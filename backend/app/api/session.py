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
from app.services import llm
from app.core.config import settings

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

    # Check if assessment already exists
    existing_session = await supabase.get_session_state(assessment_id)
    if existing_session:
        raise HTTPException(status_code=400, detail="Assessment already started")

    # Start assessment with agent
    try:
        initial_response, session_state = await assessment_agent.start_assessment(
            assessment_id=assessment_id,
            target_language=target_language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

    # Store session state in database
    await supabase.create_session_state(session_state)

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

    # Load session state from database
    session_state = await supabase.get_session_state(assessment_id)
    if not session_state:
        # Fallback: create new session if not found (for development)
        print(f"Warning: Session {assessment_id} not found, creating mock state")
        session_state = SessionState(
            assessment_id=assessment_id,
            target_language=settings.DEFAULT_TARGET_LANGUAGE,
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

    # Store updated state in database
    await supabase.update_session_state(assessment_id, updated_state)

    # If assessment concluded, store final evaluation
    if not response.should_continue:
        proficiency = await llm.calculate_overall_proficiency(updated_state)
        await supabase.store_final_evaluation(assessment_id, proficiency)

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

    session_state = await supabase.get_session_state(assessment_id)
    if not session_state:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return session_state


@router.get("/results/{assessment_id}")
async def get_results(assessment_id: str):
    """
    Get final assessment results.

    Returns:
    - CEFR proficiency level
    - Grammar/fluency scores
    - Detailed feedback per exercise
    """

    session_state = await supabase.get_session_state(assessment_id)
    if not session_state:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Calculate strengths and areas for improvement from exercises
    strengths = []
    areas_for_improvement = []
    
    for exercise in session_state.exercises_completed:
        if exercise.grammar_score and exercise.grammar_score >= 80:
            if "Strong grammar skills" not in strengths:
                strengths.append("Strong grammar skills")
        elif exercise.grammar_score and exercise.grammar_score < 60:
            if "Grammar accuracy" not in areas_for_improvement:
                areas_for_improvement.append("Grammar accuracy")
        
        if exercise.fluency_score and exercise.fluency_score >= 80:
            if "Natural conversational flow" not in strengths:
                strengths.append("Natural conversational flow")
        elif exercise.fluency_score and exercise.fluency_score < 60:
            if "Speaking fluency" not in areas_for_improvement:
                areas_for_improvement.append("Speaking fluency")
        
        if exercise.accuracy_score and exercise.accuracy_score >= 80:
            if "Accurate translations" not in strengths:
                strengths.append("Accurate translations")
        elif exercise.accuracy_score and exercise.accuracy_score < 60:
            if "Translation accuracy" not in areas_for_improvement:
                areas_for_improvement.append("Translation accuracy")

    # Default feedback if lists are empty
    if not strengths:
        strengths = ["Good effort throughout the assessment"]
    if not areas_for_improvement:
        areas_for_improvement = ["Continue practicing regularly"]

    # Generate summary feedback based on proficiency level
    level = session_state.overall_proficiency_level or "Unknown"
    level_feedback = {
        "A1": "Beginner level. Focus on building basic vocabulary and simple sentence structures.",
        "A2": "Elementary level. Continue practicing everyday conversations and common expressions.",
        "B1": "Intermediate level. Good foundation! Work on more complex grammar and idiomatic expressions.",
        "B2": "Upper intermediate. Strong skills! Focus on nuance, style, and advanced vocabulary.",
        "C1": "Advanced level. Excellent proficiency! Refine your academic and professional language use.",
        "C2": "Mastery level. Near-native proficiency. Maintain through regular immersion."
    }
    
    return {
        "assessment_id": assessment_id,
        "target_language": session_state.target_language,
        "proficiency_level": session_state.overall_proficiency_level,
        "overall_grammar_score": session_state.overall_grammar_score,
        "overall_fluency_score": session_state.overall_fluency_score,
        "exercises_completed": len(session_state.exercises_completed),
        "speaking_exercises_done": session_state.speaking_exercises_done,
        "translation_exercises_done": session_state.translation_exercises_done,
        "feedback": level_feedback.get(level, "Complete more exercises for a detailed assessment."),
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement,
        "exercises": [
            {
                "exercise_id": e.exercise_id,
                "exercise_type": e.exercise_type,
                "difficulty_level": e.difficulty_level,
                "grammar_score": e.grammar_score,
                "fluency_score": e.fluency_score,
                "accuracy_score": e.accuracy_score,
                "feedback": e.feedback,
                "errors": e.errors
            }
            for e in session_state.exercises_completed
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

    session_state = await supabase.get_session_state(assessment_id)
    if not session_state:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Calculate final proficiency
    proficiency = await llm.calculate_overall_proficiency(session_state)
    
    # Store final evaluation
    await supabase.store_final_evaluation(assessment_id, proficiency)

    return {
        "message": "Assessment ended successfully",
        "assessment_id": assessment_id,
        "proficiency_level": proficiency.get("proficiency_level"),
        "grammar_score": proficiency.get("grammar_score"),
        "fluency_score": proficiency.get("fluency_score")
    }
