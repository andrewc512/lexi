"""
LLM service for language proficiency assessment.

This service handles all LLM interactions for:
- Language evaluation (grammar, fluency, accuracy)
- Exercise generation (speaking prompts, translation passages)
- Difficulty adaptation
- Agentic decision-making
"""

from typing import List, Optional, Dict
from app.models.session import LanguageExercise, SessionState
from openai import AsyncOpenAI
from app.core.config import settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# =============================================================================
# INTERVIEW CONVERSATION FUNCTIONS
# =============================================================================

async def generate_interview_response(
    conversation_history: List[dict]
) -> str:
    """
    Generate an AI interviewer response based on conversation history.

    Args:
        conversation_history: List of {"role": "user"/"assistant", "content": "..."}

    Returns:
        AI interviewer's next question or response
    """
    try:
        # System prompt defining Lexi's personality
        system_prompt = """You are Lexi, a friendly and professional AI interviewer. Your role is to:

1. Conduct engaging technical and behavioral interviews
2. Ask thoughtful follow-up questions based on candidate responses
3. Keep questions concise and conversational
4. Be encouraging and create a comfortable atmosphere
5. Probe for details about technical skills, problem-solving, and experience
6. Keep your responses under 2-3 sentences

Remember to be warm, professional, and genuinely interested in the candidate's responses."""

        # Build messages with system prompt
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history
        ]

        # Generate response using GPT-4
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating interview response: {e}")
        # Fallback to simple response
        return "That's interesting. Can you tell me more about that?"


# =============================================================================
# LANGUAGE ASSESSMENT AGENT FUNCTIONS
# =============================================================================

async def agent_decide_next_exercise(
    session_state: SessionState,
    previous_exercise: Optional[LanguageExercise] = None
) -> dict:
    """
    Agent decides what exercise to give next based on performance.

    Analyzes:
    - Current phase (speaking_test vs translation_test)
    - Previous exercise performance
    - Current difficulty level
    - Number of exercises completed
    - Whether to adjust difficulty
    - Whether to switch phases or conclude

    Returns:
        {
            "action_type": "speaking_prompt" | "translation_prompt" |
                          "increase_difficulty" | "decrease_difficulty" |
                          "switch_phase" | "conclude",
            "reasoning": "Why this action was chosen",
            "next_phase": "translation_test" | "complete" | None,
            "difficulty_adjustment": +1 | -1 | 0
        }

    TODO: Implement with Anthropic Claude API
    """

    # STUB: Simple logic - replace with LLM
    current_phase = session_state.current_phase

    if current_phase == "intro":
        return {
            "action_type": "speaking_prompt",
            "reasoning": "Starting speaking assessment",
            "next_phase": "speaking_test",
            "difficulty_adjustment": 0
        }

    if current_phase == "speaking_test":
        if session_state.speaking_exercises_done >= 5:
            return {
                "action_type": "switch_phase",
                "reasoning": "Completed speaking assessment, moving to translation",
                "next_phase": "translation_test",
                "difficulty_adjustment": 0
            }

        # Increase difficulty if they scored well
        if previous_exercise and previous_exercise.grammar_score and previous_exercise.grammar_score > 80:
            return {
                "action_type": "speaking_prompt",
                "reasoning": "Good performance - increasing difficulty",
                "next_phase": None,
                "difficulty_adjustment": 1
            }

        return {
            "action_type": "speaking_prompt",
            "reasoning": "Continue speaking assessment",
            "next_phase": None,
            "difficulty_adjustment": 0
        }

    if current_phase == "translation_test":
        if session_state.translation_exercises_done >= 5:
            return {
                "action_type": "conclude",
                "reasoning": "Assessment complete",
                "next_phase": "complete",
                "difficulty_adjustment": 0
            }

        # Adjust difficulty based on translation accuracy
        if previous_exercise and previous_exercise.accuracy_score:
            if previous_exercise.accuracy_score > 85:
                adjustment = 1
            elif previous_exercise.accuracy_score < 60:
                adjustment = -1
            else:
                adjustment = 0

            return {
                "action_type": "translation_prompt",
                "reasoning": f"Adjusting difficulty based on score: {previous_exercise.accuracy_score}",
                "next_phase": None,
                "difficulty_adjustment": adjustment
            }

        return {
            "action_type": "translation_prompt",
            "reasoning": "Continue translation assessment",
            "next_phase": None,
            "difficulty_adjustment": 0
        }

    return {
        "action_type": "conclude",
        "reasoning": "Unknown phase",
        "next_phase": "complete",
        "difficulty_adjustment": 0
    }


async def evaluate_speaking_exercise(
    transcript: str,
    target_language: str,
    difficulty_level: int
) -> dict:
    """
    Evaluate a speaking exercise for grammar and fluency.

    Analyzes:
    - Grammar correctness
    - Vocabulary appropriateness
    - Sentence structure
    - Fluency/naturalness

    Returns:
        {
            "grammar_score": 85.0,  # 0-100
            "fluency_score": 78.0,  # 0-100
            "feedback": "Good use of past tense, but watch subject-verb agreement",
            "errors": ["'I goes' should be 'I go'", "Missing article before 'car'"],
            "strengths": ["Natural sentence flow", "Good vocabulary range"]
        }

    TODO: Implement with Claude API for grammar checking
    """

    # STUB: Mock evaluation
    return {
        "grammar_score": 75.0,
        "fluency_score": 80.0,
        "feedback": "Generally good, but some minor grammar issues.",
        "errors": [
            "Subject-verb agreement error in sentence 2",
            "Incorrect preposition usage"
        ],
        "strengths": [
            "Natural conversational flow",
            "Good vocabulary variety"
        ]
    }


async def evaluate_translation_exercise(
    original_passage: str,
    user_translation: str,
    source_language: str,
    target_language: str,
    difficulty_level: int
) -> dict:
    """
    Evaluate a translation exercise for accuracy.

    Analyzes:
    - Translation accuracy
    - Meaning preservation
    - Grammar in target language
    - Idiom/cultural understanding

    Returns:
        {
            "accuracy_score": 88.0,  # 0-100
            "grammar_score": 85.0,
            "feedback": "Accurate translation with good understanding of context",
            "errors": ["'hacer' translated too literally", "Tense mismatch"],
            "correct_translation": "The suggested optimal translation..."
        }

    TODO: Implement with Claude API for translation evaluation
    """

    # STUB: Mock evaluation
    return {
        "accuracy_score": 82.0,
        "grammar_score": 78.0,
        "feedback": "Good overall translation, captured main meaning well.",
        "errors": [
            "Idiomatic expression not translated naturally",
            "Minor tense inconsistency"
        ],
        "correct_translation": "A more natural translation would be: ..."
    }


async def generate_speaking_prompt(
    target_language: str,
    difficulty_level: int,
    previous_prompts: List[str] = []
) -> str:
    """
    Generate a speaking exercise prompt at the appropriate difficulty.

    Difficulty levels:
    - 1-3: Simple questions (present tense, basic vocabulary)
    - 4-6: Moderate questions (past/future tense, common topics)
    - 7-10: Complex questions (subjunctive, abstract topics)

    TODO: Implement with Claude to generate varied prompts
    """

    # STUB: Hardcoded prompts by difficulty
    prompts_by_level = {
        1: "What is your name and where are you from?",
        2: "Describe your daily routine.",
        3: "Talk about your favorite hobby.",
        4: "Describe something interesting you did last week.",
        5: "What are your plans for the future?",
        6: "Explain a challenge you've overcome.",
        7: "Discuss the pros and cons of social media.",
        8: "Describe a hypothetical situation where you had to make a difficult decision.",
        9: "Analyze the impact of technology on modern society.",
        10: "Debate whether artificial intelligence will ultimately benefit or harm humanity."
    }

    return prompts_by_level.get(difficulty_level, prompts_by_level[5])


async def generate_translation_passage(
    source_language: str,
    target_language: str,
    difficulty_level: int,
    previous_passages: List[str] = []
) -> str:
    """
    Generate a passage to translate at the appropriate difficulty.

    Difficulty levels:
    - 1-3: Simple sentences (present tense, common words)
    - 4-6: Moderate passages (mixed tenses, everyday topics)
    - 7-10: Complex passages (idioms, cultural references, technical vocab)

    TODO: Implement with Claude to generate varied passages
    """

    # STUB: Hardcoded passages by difficulty
    passages = {
        1: "The cat is black. It sleeps on the sofa.",
        2: "Yesterday I went to the market. I bought apples and bread.",
        3: "My family lives in a small house near the beach. We love to swim in summer.",
        4: "Last year, I traveled to Spain for the first time. The food was incredible and the people were very friendly.",
        5: "If I had more time, I would learn to play the guitar. Music has always been important to me.",
        6: "The company announced that it would be expanding into new markets next quarter, which surprised many investors.",
        7: "Despite the challenges posed by climate change, renewable energy adoption continues to accelerate worldwide.",
        8: "The author's subtle use of metaphor throughout the novel serves to underscore the protagonist's internal struggle.",
        9: "Neuroscientists have discovered that synaptic plasticity plays a crucial role in memory consolidation during REM sleep.",
        10: "The geopolitical ramifications of this diplomatic overture could potentially reshape the balance of power across the entire region."
    }

    return passages.get(difficulty_level, passages[5])


async def calculate_overall_proficiency(
    session_state: SessionState
) -> dict:
    """
    Calculate overall proficiency level based on all exercises.

    Returns CEFR level (A1, A2, B1, B2, C1, C2) and scores.

    TODO: Implement proper CEFR scoring algorithm
    """

    if not session_state.exercises_completed:
        return {
            "proficiency_level": "Unknown",
            "grammar_score": 0.0,
            "fluency_score": 0.0
        }

    # Average scores from all exercises
    grammar_scores = [e.grammar_score for e in session_state.exercises_completed if e.grammar_score]
    fluency_scores = [e.fluency_score for e in session_state.exercises_completed if e.fluency_score]

    avg_grammar = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0
    avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0

    # Simple CEFR mapping (stub - should be more sophisticated)
    avg_score = (avg_grammar + avg_fluency) / 2
    if avg_score >= 90:
        level = "C2"
    elif avg_score >= 80:
        level = "C1"
    elif avg_score >= 70:
        level = "B2"
    elif avg_score >= 60:
        level = "B1"
    elif avg_score >= 50:
        level = "A2"
    else:
        level = "A1"

    return {
        "proficiency_level": level,
        "grammar_score": avg_grammar,
        "fluency_score": avg_fluency
    }
