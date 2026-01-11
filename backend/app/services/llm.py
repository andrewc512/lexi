"""
LLM service for language proficiency assessment.

This service handles all LLM interactions for:
- Language evaluation (grammar, fluency, accuracy)
- Exercise generation (speaking prompts, translation passages)
- Difficulty adaptation
- Agentic decision-making
"""

import json
from typing import List, Optional, Dict
from datetime import datetime, timezone
from app.models.session import LanguageExercise, SessionState
from openai import AsyncOpenAI
from app.core.config import settings

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# =============================================================================
# INTERVIEW CONVERSATION FUNCTIONS
# =============================================================================

async def generate_interview_response(
    conversation_history: List[dict],
    target_language: str
) -> str:
    """
    Generate an AI interviewer response based on conversation history.

    Args:
        conversation_history: List of {"role": "user"/"assistant", "content": "..."}
        target_language: The language being assessed (e.g., "Spanish", "French", "Mandarin")

    Returns:
        AI interviewer's next question or response
    """
    try:
        # System prompt defining Lexi's personality
        system_prompt = f"""You are Lexi, a friendly and encouraging language proficiency assessor specializing in {target_language}. Your role is to:

1. Assess the user's {target_language} language proficiency through natural conversation
2. Evaluate their speaking ability, grammar, vocabulary, and fluency in {target_language}
3. Ask natural follow-up questions in {target_language} to assess their skills at different levels
4. Create a comfortable, low-pressure environment that encourages the user to speak naturally
5. Adapt your questions based on their proficiency level (simpler if they struggle, more complex if they excel)
6. Keep your responses under 2-3 sentences to encourage them to speak more
7. Be supportive and focus on helping them demonstrate their best {target_language} abilities

IMPORTANT LANGUAGE INSTRUCTIONS:
- Your FIRST message should be in English to welcome them and explain the assessment
- ALL subsequent messages MUST be in {target_language} only
- Do not translate or provide English explanations after the first message
- Immerse them fully in {target_language} to properly assess their proficiency

Remember to be warm, patient, and genuinely interested in helping the user showcase their language proficiency."""

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
    - Time spent in each phase (1 min speaking, 1.5 min translation)
    - Previous exercise performance
    - Current difficulty level
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
    current_time = datetime.utcnow()

    # Time limits for each phase
    SPEAKING_DURATION_SECONDS = 120  # 2 minutes
    TRANSLATION_DURATION_SECONDS = 120  # 2 minutes

    if current_phase == "intro":
        return {
            "action_type": "speaking_prompt",
            "reasoning": "Starting speaking assessment",
            "next_phase": "speaking_test",
            "difficulty_adjustment": 0
        }

    if current_phase == "speaking_test":
        # Check if speaking phase time is up
        if session_state.speaking_phase_start:
            phase_start = datetime.fromisoformat(session_state.speaking_phase_start)
            elapsed_seconds = (current_time - phase_start).total_seconds()

            if elapsed_seconds >= SPEAKING_DURATION_SECONDS:
                return {
                    "action_type": "switch_phase",
                    "reasoning": f"Speaking assessment time complete ({elapsed_seconds:.0f}s), moving to translation",
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
        # Check if translation phase time is up
        if session_state.translation_phase_start:
            phase_start = datetime.fromisoformat(session_state.translation_phase_start)
            elapsed_seconds = (current_time - phase_start).total_seconds()

            if elapsed_seconds >= TRANSLATION_DURATION_SECONDS:
                return {
                    "action_type": "conclude",
                    "reasoning": f"Translation assessment time complete ({elapsed_seconds:.0f}s)",
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
    Evaluate a speaking exercise for grammar and fluency using OpenAI.

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
    """
    
    # Handle empty or very short transcripts
    if not transcript or len(transcript.strip()) < 3:
        return {
            "grammar_score": 0.0,
            "fluency_score": 0.0,
            "feedback": "No speech detected or response was too short.",
            "errors": ["No meaningful response provided"],
            "strengths": []
        }
    
    try:
        system_prompt = f"""You are an expert {target_language} language evaluator. Analyze the following speech transcript and provide a detailed evaluation.

Difficulty level: {difficulty_level}/10 (1=beginner, 10=advanced)

Evaluate based on:
1. Grammar correctness - Are verb conjugations, gender agreements, sentence structures correct?
2. Fluency/Naturalness - Does it sound natural? Is the flow smooth? Is vocabulary appropriate?
3. Vocabulary usage - Is the vocabulary appropriate for the difficulty level?

Be encouraging but honest. Adjust your expectations based on the difficulty level - be more lenient for beginners.

You MUST respond in this exact JSON format:
{{
    "grammar_score": <number 0-100>,
    "fluency_score": <number 0-100>,
    "feedback": "<2-3 sentence summary of their performance>",
    "errors": ["<specific error 1>", "<specific error 2>"],
    "strengths": ["<strength 1>", "<strength 2>"]
}}

If there are no errors, use an empty array: "errors": []
If there are no notable strengths, use: "strengths": ["Good effort"]
Always include at least one item in strengths to be encouraging."""

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate this {target_language} speech:\n\n\"{transcript}\""}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        # Sometimes the model wraps it in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        evaluation = json.loads(response_text)
        
        # Ensure all required fields exist with proper types
        return {
            "grammar_score": float(evaluation.get("grammar_score", 50.0)),
            "fluency_score": float(evaluation.get("fluency_score", 50.0)),
            "feedback": str(evaluation.get("feedback", "Evaluation completed.")),
            "errors": list(evaluation.get("errors", [])),
            "strengths": list(evaluation.get("strengths", ["Good effort"]))
        }
        
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        # Return a reasonable default if JSON parsing fails
        return {
            "grammar_score": 60.0,
            "fluency_score": 60.0,
            "feedback": "Your response was received. Keep practicing!",
            "errors": [],
            "strengths": ["Good effort in attempting the exercise"]
        }
    except Exception as e:
        print(f"Error evaluating speaking exercise: {e}")
        # Return a fallback response
        return {
            "grammar_score": 50.0,
            "fluency_score": 50.0,
            "feedback": "We couldn't fully evaluate your response. Please try again.",
            "errors": [],
            "strengths": ["Thank you for participating"]
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
    """
    
    # Handle empty or very short translations
    if not user_translation or len(user_translation.strip()) < 3:
        return {
            "accuracy_score": 0.0,
            "grammar_score": 0.0,
            "feedback": "No translation provided or response was too short.",
            "errors": ["No meaningful translation provided"],
            "correct_translation": "Please provide a translation of the passage."
        }
    
    try:
        system_prompt = f"""You are an expert {source_language} to {target_language} translation evaluator. Analyze the user's translation and provide a detailed evaluation.

Original passage ({source_language}):
"{original_passage}"

Difficulty level: {difficulty_level}/10 (1=beginner, 10=advanced)

Evaluate based on:
1. Accuracy - How well does the translation capture the meaning of the original? Are key ideas preserved?
2. Grammar - Is the {target_language} grammatically correct?
3. Naturalness - Does the translation sound natural in {target_language}? Are idioms handled well?
4. Completeness - Are all parts of the original passage translated?

Be encouraging but honest. Adjust your expectations based on the difficulty level - be more lenient for beginners.

You MUST respond in this exact JSON format:
{{
    "accuracy_score": <number 0-100>,
    "grammar_score": <number 0-100>,
    "feedback": "<2-3 sentence summary of their translation quality>",
    "errors": ["<specific error 1>", "<specific error 2>"],
    "correct_translation": "<the ideal/suggested translation of the passage>"
}}

If the translation is perfect, use an empty array: "errors": []
Always provide an encouraging and constructive feedback message."""

        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Evaluate this translation to {target_language}:\n\n\"{user_translation}\""}
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        # Sometimes the model wraps it in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        evaluation = json.loads(response_text)
        
        # Ensure all required fields exist with proper types
        return {
            "accuracy_score": float(evaluation.get("accuracy_score", 50.0)),
            "grammar_score": float(evaluation.get("grammar_score", 50.0)),
            "feedback": str(evaluation.get("feedback", "Translation evaluated.")),
            "errors": list(evaluation.get("errors", [])),
            "correct_translation": str(evaluation.get("correct_translation", ""))
        }
        
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response as JSON: {e}")
        # Return a reasonable default if JSON parsing fails
        return {
            "accuracy_score": 60.0,
            "grammar_score": 60.0,
            "feedback": "Your translation was received. Keep practicing!",
            "errors": [],
            "correct_translation": "We couldn't generate a suggested translation."
        }
    except Exception as e:
        print(f"Error evaluating translation exercise: {e}")
        # Return a fallback response
        return {
            "accuracy_score": 50.0,
            "grammar_score": 50.0,
            "feedback": "We couldn't fully evaluate your translation. Please try again.",
            "errors": [],
            "correct_translation": ""
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
    Generate a passage in the source language to translate to the target language.

    Difficulty levels:
    - 1-3: Simple sentences (present tense, common words)
    - 4-6: Moderate passages (mixed tenses, everyday topics)
    - 7-10: Complex passages (idioms, cultural references, technical vocab)

    Args:
        source_language: Language to generate the passage in (e.g., "Spanish", "Korean")
        target_language: Language to translate to (usually "English")
        difficulty_level: 1-10 difficulty rating
        previous_passages: Previously used passages to avoid repetition

    Returns:
        A passage written in the source_language
    """

    # Map difficulty to complexity description
    complexity_map = {
        1: "very simple sentences with present tense and basic vocabulary (beginner A1 level)",
        2: "simple sentences with common past and future tenses (beginner A2 level)",
        3: "simple everyday topics with basic grammar structures (elementary A2 level)",
        4: "moderate complexity with mixed tenses about everyday situations (intermediate B1 level)",
        5: "moderate complexity with some idiomatic expressions (intermediate B1 level)",
        6: "moderately complex passages with varied vocabulary (upper-intermediate B2 level)",
        7: "complex passages with sophisticated vocabulary and idioms (upper-intermediate B2 level)",
        8: "advanced passages with nuanced language and cultural references (advanced C1 level)",
        9: "very advanced passages with technical or academic vocabulary (advanced C1 level)",
        10: "highly sophisticated passages with complex structures and abstract concepts (mastery C2 level)"
    }

    complexity = complexity_map.get(difficulty_level, complexity_map[5])

    # Build prompt to avoid repetition
    avoid_topics = ""
    if previous_passages:
        avoid_topics = f"\n\nIMPORTANT: Do NOT write about topics similar to these previous passages:\n" + "\n".join(f"- {p[:100]}..." for p in previous_passages[-3:])

    system_prompt = f"""You are a language assessment expert. Generate a reading passage in {source_language} that is appropriate for translation practice.

Difficulty level: {difficulty_level}/10 - {complexity}

Requirements:
1. Write ONLY in {source_language} (not {target_language})
2. Make it {complexity}
3. Length: 2-4 sentences for levels 1-3, 3-5 sentences for levels 4-7, 4-6 sentences for levels 8-10
4. Topics should be interesting and varied (culture, daily life, nature, technology, history, etc.)
5. Use natural, authentic {source_language} - not simplified or overly formal{avoid_topics}

Return ONLY the {source_language} passage text, nothing else."""

    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a {source_language} reading passage at difficulty level {difficulty_level}."}
            ],
            temperature=0.8,  # Higher temperature for more variety
            max_tokens=300
        )

        passage = response.choices[0].message.content.strip()

        # Remove any quotation marks that might wrap the passage
        if passage.startswith('"') and passage.endswith('"'):
            passage = passage[1:-1]
        if passage.startswith("'") and passage.endswith("'"):
            passage = passage[1:-1]

        return passage

    except Exception as e:
        print(f"Error generating translation passage: {e}")
        # Fallback to a simple default
        fallback_passages = {
            "Spanish": "El gato duerme en el sofá. Es negro y muy tranquilo.",
            "French": "Le chat dort sur le canapé. Il est noir et très calme.",
            "German": "Die Katze schläft auf dem Sofa. Sie ist schwarz und sehr ruhig.",
            "Korean": "고양이가 소파에서 자고 있습니다. 검은색이고 매우 조용합니다.",
            "Japanese": "猫はソファーで寝ています。黒くてとても静かです。",
            "Chinese": "猫在沙发上睡觉。它是黑色的，非常安静。",
            "Italian": "Il gatto dorme sul divano. È nero e molto tranquillo.",
            "Portuguese": "O gato dorme no sofá. Ele é preto e muito calmo."
        }
        return fallback_passages.get(source_language, "The cat sleeps on the sofa.")


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
