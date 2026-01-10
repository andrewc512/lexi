"""
Stateless Language Assessment Agent - Orchestrates language proficiency testing.

This agent takes audio/text input + session state, evaluates language ability,
and returns exercises + feedback. It maintains NO internal state.
"""

from typing import Tuple, Optional
from uuid import uuid4
from app.models.session import (
    SessionState,
    LanguageExercise,
    AgentResponse,
    AgentAction
)
from app.services import stt, llm, tts


class LanguageAssessmentAgent:
    """
    Stateless agent that orchestrates language assessments.

    Responsibilities:
    1. Process speaking exercises (audio → transcription → grammar evaluation)
    2. Process translation exercises (passage → user translation → accuracy check)
    3. Adapt difficulty based on performance
    4. Generate appropriate exercises
    5. Track progress and calculate proficiency level

    The agent is STATELESS - all state is in SessionState and stored externally.
    """

    def __init__(self):
        """Initialize with no state - just service dependencies."""
        pass

    async def process_exercise(
        self,
        session_state: SessionState,
        audio_bytes: Optional[bytes] = None,
        text_response: Optional[str] = None
    ) -> Tuple[AgentResponse, SessionState]:
        """
        Main agentic loop - processes one language exercise.

        Args:
            session_state: Current session state (from database)
            audio_bytes: Raw audio for speaking/translation exercises
            text_response: Text translation (alternative to audio)

        Returns:
            (agent_response, updated_session_state)

        Flow:
            1. If audio provided, transcribe to text
            2. Evaluate previous exercise (if exists)
            3. Decide next exercise type and difficulty
            4. Generate new exercise (prompt or passage)
            5. Return evaluation + new exercise
        """

        evaluated_exercise = None

        # Step 1: Process previous exercise if audio/text provided
        if audio_bytes or text_response:
            evaluated_exercise = await self._evaluate_previous_exercise(
                session_state=session_state,
                audio_bytes=audio_bytes,
                text_response=text_response
            )

            # Add evaluated exercise to state
            session_state = session_state.add_exercise(evaluated_exercise)

        # Step 2: Decide next exercise
        action_decision = await llm.agent_decide_next_exercise(
            session_state=session_state,
            previous_exercise=evaluated_exercise
        )

        action = AgentAction(**action_decision)

        # Step 3: Adjust difficulty
        new_difficulty = session_state.current_difficulty
        if action.difficulty_adjustment:
            new_difficulty = max(1, min(10, new_difficulty + action.difficulty_adjustment))

        # Step 4: Generate next exercise or conclude
        next_exercise_data = await self._generate_next_exercise(
            action=action,
            session_state=session_state,
            difficulty=new_difficulty
        )

        # Step 5: Build agent response
        agent_response = AgentResponse(
            text=next_exercise_data.get("instruction_text", ""),
            audio_url=next_exercise_data.get("audio_url"),
            action=action,
            should_continue=(action.action_type != "conclude"),
            speaking_prompt=next_exercise_data.get("speaking_prompt"),
            translation_passage=next_exercise_data.get("translation_passage"),
            passage_language=next_exercise_data.get("passage_language"),
            difficulty_level=new_difficulty,
            evaluation=self._format_evaluation(evaluated_exercise) if evaluated_exercise else None
        )

        # Step 6: Update session state
        updated_state = SessionState(
            **session_state.model_dump(exclude={"current_phase", "current_difficulty", "last_updated"}),
            current_phase=action.next_phase if action.next_phase else session_state.current_phase,
            current_difficulty=new_difficulty
        )

        # Add insight
        if action.reasoning:
            updated_state.insights.append(action.reasoning)

        return agent_response, updated_state

    async def _evaluate_previous_exercise(
        self,
        session_state: SessionState,
        audio_bytes: Optional[bytes],
        text_response: Optional[str]
    ) -> LanguageExercise:
        """
        Evaluate the user's response to the previous exercise.
        """

        # Get the last exercise from state (what they were responding to)
        # For now, we'll create a placeholder - in real impl, track "current_exercise"
        current_phase = session_state.current_phase
        exercise_type = "speaking" if current_phase == "speaking_test" else "translation"

        # Transcribe audio if provided
        transcript = None
        if audio_bytes:
            transcript = await stt.transcribe_audio(
                audio_bytes,
                language=session_state.target_language if exercise_type == "speaking" else "English"
            )
        else:
            transcript = text_response

        # Create exercise object
        exercise = LanguageExercise(
            exercise_id=f"ex_{uuid4().hex[:8]}",
            exercise_type=exercise_type,
            difficulty_level=session_state.current_difficulty,
            transcript=transcript,
            timestamp=""
        )

        # Evaluate based on type
        if exercise_type == "speaking":
            evaluation = await llm.evaluate_speaking_exercise(
                transcript=transcript,
                target_language=session_state.target_language,
                difficulty_level=session_state.current_difficulty
            )

            exercise.grammar_score = evaluation.get("grammar_score")
            exercise.fluency_score = evaluation.get("fluency_score")
            exercise.feedback = evaluation.get("feedback")
            exercise.errors = evaluation.get("errors", [])

        else:  # translation
            # For translation, we need the original passage (should be tracked in state)
            # For now, using mock passage
            evaluation = await llm.evaluate_translation_exercise(
                original_passage="Mock passage",  # TODO: Track current exercise in state
                user_translation=transcript,
                source_language=session_state.target_language,
                target_language="English",
                difficulty_level=session_state.current_difficulty
            )

            exercise.accuracy_score = evaluation.get("accuracy_score")
            exercise.grammar_score = evaluation.get("grammar_score")
            exercise.feedback = evaluation.get("feedback")
            exercise.errors = evaluation.get("errors", [])

        return exercise

    async def _generate_next_exercise(
        self,
        action: AgentAction,
        session_state: SessionState,
        difficulty: int
    ) -> dict:
        """
        Generate the next exercise based on agent's decision.
        """

        if action.action_type == "conclude":
            # Calculate final proficiency
            proficiency = await llm.calculate_overall_proficiency(session_state)

            return {
                "instruction_text": f"Assessment complete! Your {session_state.target_language} proficiency level is {proficiency['proficiency_level']}. "
                                   f"Grammar: {proficiency['grammar_score']:.1f}%, Fluency: {proficiency['fluency_score']:.1f}%",
                "audio_url": None
            }

        elif action.action_type == "speaking_prompt" or (
            action.action_type == "switch_phase" and action.next_phase == "speaking_test"
        ):
            # Generate speaking prompt
            prompt = await llm.generate_speaking_prompt(
                target_language=session_state.target_language,
                difficulty_level=difficulty,
                previous_prompts=[e.prompt for e in session_state.exercises_completed if e.prompt]
            )

            return {
                "instruction_text": f"Please answer the following question in {session_state.target_language}:",
                "speaking_prompt": prompt,
                "audio_url": None
            }

        elif action.action_type == "translation_prompt" or (
            action.action_type == "switch_phase" and action.next_phase == "translation_test"
        ):
            # Generate translation passage
            passage = await llm.generate_translation_passage(
                source_language=session_state.target_language,
                target_language="English",
                difficulty_level=difficulty,
                previous_passages=[e.passage for e in session_state.exercises_completed if e.passage]
            )

            return {
                "instruction_text": "Please translate the following passage to English:",
                "translation_passage": passage,
                "passage_language": session_state.target_language,
                "audio_url": None
            }

        else:
            return {
                "instruction_text": "Please continue.",
                "audio_url": None
            }

    def _format_evaluation(self, exercise: LanguageExercise) -> dict:
        """Format exercise evaluation for response."""
        eval_dict = {
            "grammar_score": exercise.grammar_score,
            "fluency_score": exercise.fluency_score,
            "accuracy_score": exercise.accuracy_score,
            "feedback": exercise.feedback,
            "errors": exercise.errors
        }

        # Remove None values
        return {k: v for k, v in eval_dict.items() if v is not None}

    async def start_assessment(
        self,
        assessment_id: str,
        target_language: str
    ) -> Tuple[AgentResponse, SessionState]:
        """
        Start a new language assessment session.

        Returns:
            (initial_prompt, initial_session_state)
        """

        # Create initial session state
        session_state = SessionState(
            assessment_id=assessment_id,
            target_language=target_language,
            current_phase="intro",
            current_difficulty=1
        )

        # Generate first speaking prompt
        prompt = await llm.generate_speaking_prompt(
            target_language=target_language,
            difficulty_level=1
        )

        # Build response
        response = AgentResponse(
            text=f"Welcome to your {target_language} proficiency assessment! We'll start with speaking exercises. Please answer in {target_language}:",
            audio_url=None,
            action=AgentAction(
                action_type="speaking_prompt",
                reasoning="Starting assessment with speaking test",
                next_phase="speaking_test",
                difficulty_adjustment=0
            ),
            should_continue=True,
            speaking_prompt=prompt,
            difficulty_level=1
        )

        # Update phase
        updated_state = SessionState(
            **session_state.model_dump(exclude={"current_phase"}),
            current_phase="speaking_test"
        )

        return response, updated_state


# Singleton instance (stateless, so safe to share)
assessment_agent = LanguageAssessmentAgent()
