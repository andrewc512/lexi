"""Session state models for language proficiency assessment."""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class LanguageExercise(BaseModel):
    """A single language assessment exercise (speaking or translation)."""
    exercise_id: str
    exercise_type: Literal["speaking", "translation"]
    difficulty_level: int  # 1-10 scale
    prompt: Optional[str] = None  # For speaking: question to answer
    passage: Optional[str] = None  # For translation: text to translate
    passage_language: Optional[str] = None  # e.g., "Spanish", "French"
    target_language: str = "English"  # Language to respond in

    # User's response
    audio_url: Optional[str] = None
    transcript: Optional[str] = None  # STT of what they said
    translation: Optional[str] = None  # Their translation attempt

    # Evaluation
    grammar_score: Optional[float] = None  # 0-100
    fluency_score: Optional[float] = None  # 0-100
    accuracy_score: Optional[float] = None  # 0-100 (for translation)
    feedback: Optional[str] = None
    errors: List[str] = []  # Specific grammar/vocabulary errors

    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SessionState(BaseModel):
    """
    Complete state of a language assessment session.
    This is passed to the agent and stored in the database.
    """
    assessment_id: str
    target_language: str  # Language being assessed (e.g., "Spanish")

    # Test phases
    current_phase: Literal[
        "intro",           # Welcome and instructions
        "speaking_test",   # Conversational speaking assessment
        "translation_test", # Passage translation assessment
        "complete"         # Assessment finished
    ] = "intro"

    # Exercise tracking
    exercises_completed: List[LanguageExercise] = []
    current_difficulty: int = 1  # Starts at 1, increases based on performance
    speaking_exercises_done: int = 0
    translation_exercises_done: int = 0

    # Time tracking
    speaking_phase_start: Optional[str] = None  # ISO timestamp when speaking phase started
    translation_phase_start: Optional[str] = None  # ISO timestamp when translation phase started

    # Scoring
    overall_grammar_score: Optional[float] = None
    overall_fluency_score: Optional[float] = None
    overall_proficiency_level: Optional[str] = None  # A1, A2, B1, B2, C1, C2

    # Metadata
    insights: List[str] = []  # Agent's observations
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    def add_exercise(self, exercise: LanguageExercise) -> "SessionState":
        """Add completed exercise and update counters."""
        updated = SessionState(
            **self.model_dump(exclude={
                "exercises_completed",
                "speaking_exercises_done",
                "translation_exercises_done",
                "last_updated"
            }),
            exercises_completed=self.exercises_completed + [exercise],
            speaking_exercises_done=self.speaking_exercises_done + (
                1 if exercise.exercise_type == "speaking" else 0
            ),
            translation_exercises_done=self.translation_exercises_done + (
                1 if exercise.exercise_type == "translation" else 0
            ),
            last_updated=datetime.utcnow().isoformat()
        )
        return updated


class AgentAction(BaseModel):
    """Decision made by the agent about what to do next."""
    action_type: Literal[
        "speaking_prompt",    # Give speaking exercise
        "translation_prompt", # Give translation exercise
        "increase_difficulty", # Move to harder exercises
        "decrease_difficulty", # Move to easier exercises
        "switch_phase",       # Move from speaking to translation test
        "conclude"            # End assessment
    ]
    reasoning: str  # Why the agent made this decision
    next_phase: Optional[str] = None  # If transitioning phases
    difficulty_adjustment: Optional[int] = None  # +1, -1, or 0


class AgentResponse(BaseModel):
    """Response from the agent after processing an exercise."""
    text: str  # Instructions or feedback
    audio_url: Optional[str] = None  # TTS audio URL
    action: AgentAction
    should_continue: bool  # Whether assessment should continue

    # Exercise prompts
    speaking_prompt: Optional[str] = None  # Question to answer
    translation_passage: Optional[str] = None  # Text to translate
    passage_language: Optional[str] = None  # Source language
    difficulty_level: Optional[int] = None

    # Evaluation of previous exercise
    evaluation: Optional[dict] = None  # Detailed scoring and feedback


class AssessmentTurnRequest(BaseModel):
    """Request payload for a single assessment turn."""
    assessment_id: str
    # Audio will come as UploadFile in endpoint
    # For translation exercises, text can come as form data


class AssessmentTurnResponse(BaseModel):
    """Response payload for a single assessment turn."""
    agent_response: AgentResponse
    session_state: SessionState
    exercises_completed: int
    current_phase: str
