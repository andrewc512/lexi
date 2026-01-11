"""
Reading Assessment Service

Manages the reading comprehension portion of the language interview:
- Tracks conversation time (3 minutes speaking, then transition to reading)
- Displays text passages in target language
- User translates to English (via speech or text)
- Evaluates reading comprehension and translation accuracy
"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.services import llm, stt
import time


class ReadingAssessmentManager:
    """
    Manages reading assessment phase during interviews.

    Timeline:
    - 0-3 minutes: Normal conversation in target language
    - 3 minutes: Transition message ("Now let's move to the reading portion...")
    - 3+ minutes: Reading assessment (display text, user translates)
    """

    # Duration constants (in seconds)
    CONVERSATION_DURATION = 60  # 1 minute (for testing)
    READING_DURATION = 90  # 1:30 minutes (for testing)

    def __init__(self):
        """Initialize the reading assessment manager."""
        self.reading_passages_cache = {}  # Cache generated passages

    def should_transition_to_reading(
        self,
        start_time: float,
        current_time: Optional[float] = None
    ) -> bool:
        """
        Check if it's time to transition from conversation to reading.

        Args:
            start_time: Interview start timestamp (unix timestamp)
            current_time: Current timestamp (defaults to now)

        Returns:
            True if conversation duration has elapsed, False otherwise
        """
        if current_time is None:
            current_time = time.time()

        elapsed = current_time - start_time
        return elapsed >= self.CONVERSATION_DURATION

    def should_end_reading(
        self,
        reading_start_time: float,
        current_time: Optional[float] = None
    ) -> bool:
        """
        Check if the reading phase should end.

        Args:
            reading_start_time: Reading phase start timestamp (unix timestamp)
            current_time: Current timestamp (defaults to now)

        Returns:
            True if reading duration has elapsed, False otherwise
        """
        if current_time is None:
            current_time = time.time()

        elapsed = current_time - reading_start_time
        return elapsed >= self.READING_DURATION

    def get_transition_message(self, target_language: str) -> str:
        """
        Get the message to transition from conversation to reading.

        Args:
            target_language: The language being assessed

        Returns:
            Transition message to announce reading portion
        """
        return (
            f"Alright! We've had a great conversation. "
            f"Now we're going to move to the reading portion of the evaluation. "
            f"I'll show you some text in {target_language}, and I'd like you to "
            f"read it and then translate it to English. Ready?"
        )

    async def generate_reading_passage(
        self,
        target_language: str,
        difficulty_level: int,
        previous_passages: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Generate a reading passage in the target language.

        Args:
            target_language: Language for the passage
            difficulty_level: 1-10 difficulty rating
            previous_passages: Previously used passages to avoid repetition

        Returns:
            {
                "passage": "Text in target language...",
                "topic": "Brief description of topic",
                "difficulty": 5
            }
        """
        # Use existing LLM function but customize for reading comprehension
        passage_text = await llm.generate_translation_passage(
            source_language=target_language,
            target_language="English",
            difficulty_level=difficulty_level,
            previous_passages=previous_passages or []
        )

        return {
            "passage": passage_text,
            "topic": "General text",  # Could enhance with topic detection
            "difficulty": difficulty_level
        }

    async def evaluate_reading_translation(
        self,
        original_passage: str,
        user_translation: str,
        target_language: str,
        difficulty_level: int
    ) -> Dict:
        """
        Evaluate the user's translation of a reading passage.

        Args:
            original_passage: Original text in target language
            user_translation: User's English translation
            target_language: Source language
            difficulty_level: Passage difficulty (1-10)

        Returns:
            {
                "comprehension_score": 85.0,  # 0-100
                "accuracy_score": 82.0,       # 0-100
                "grammar_score": 88.0,        # 0-100 (of English translation)
                "feedback": "Good comprehension...",
                "errors": ["Missed nuance in...", "Word X means..."],
                "correct_translation": "Suggested translation...",
                "strengths": ["Captured main idea", "Good grammar"]
            }
        """
        # Use existing translation evaluation
        evaluation = await llm.evaluate_translation_exercise(
            original_passage=original_passage,
            user_translation=user_translation,
            source_language=target_language,
            target_language="English",
            difficulty_level=difficulty_level
        )

        # Add comprehension score (same as accuracy for now)
        evaluation["comprehension_score"] = evaluation.get("accuracy_score", 0)

        # Add strengths field if not present
        if "strengths" not in evaluation:
            evaluation["strengths"] = []

        return evaluation

    async def process_audio_translation(
        self,
        audio_bytes: bytes,
        original_passage: str,
        target_language: str,
        difficulty_level: int
    ) -> Dict:
        """
        Process audio translation of a reading passage.

        Args:
            audio_bytes: Audio recording of user's translation
            original_passage: Original passage in target language
            target_language: Source language
            difficulty_level: Passage difficulty

        Returns:
            Evaluation results with transcript included
        """
        # Transcribe audio (should be in English)
        transcript = await stt.transcribe_audio(
            audio_bytes,
            language="English"
        )

        if not transcript or not transcript.strip():
            return {
                "error": "Could not transcribe audio. Please try again.",
                "transcript": None
            }

        # Evaluate the translation
        evaluation = await self.evaluate_reading_translation(
            original_passage=original_passage,
            user_translation=transcript,
            target_language=target_language,
            difficulty_level=difficulty_level
        )

        # Add transcript to results
        evaluation["transcript"] = transcript

        return evaluation

    def calculate_reading_proficiency(
        self,
        reading_evaluations: List[Dict]
    ) -> Dict:
        """
        Calculate overall reading proficiency from multiple evaluations.

        Args:
            reading_evaluations: List of evaluation results

        Returns:
            {
                "reading_level": "B2",
                "comprehension_score": 84.0,
                "accuracy_score": 81.0,
                "overall_feedback": "Strong reading comprehension..."
            }
        """
        if not reading_evaluations:
            return {
                "reading_level": "Unknown",
                "comprehension_score": 0.0,
                "accuracy_score": 0.0,
                "overall_feedback": "No reading exercises completed"
            }

        # Calculate averages
        comprehension_scores = [
            e.get("comprehension_score", 0)
            for e in reading_evaluations
            if e.get("comprehension_score") is not None
        ]

        accuracy_scores = [
            e.get("accuracy_score", 0)
            for e in reading_evaluations
            if e.get("accuracy_score") is not None
        ]

        avg_comprehension = (
            sum(comprehension_scores) / len(comprehension_scores)
            if comprehension_scores else 0
        )

        avg_accuracy = (
            sum(accuracy_scores) / len(accuracy_scores)
            if accuracy_scores else 0
        )

        # Map to CEFR level
        avg_score = (avg_comprehension + avg_accuracy) / 2

        if avg_score >= 90:
            level = "C2"
            feedback = "Exceptional reading comprehension with near-native accuracy"
        elif avg_score >= 80:
            level = "C1"
            feedback = "Strong reading comprehension with high accuracy"
        elif avg_score >= 70:
            level = "B2"
            feedback = "Good reading comprehension with solid translation skills"
        elif avg_score >= 60:
            level = "B1"
            feedback = "Adequate reading comprehension with room for improvement"
        elif avg_score >= 50:
            level = "A2"
            feedback = "Basic reading comprehension, continue practicing"
        else:
            level = "A1"
            feedback = "Beginner reading level, needs significant practice"

        return {
            "reading_level": level,
            "comprehension_score": avg_comprehension,
            "accuracy_score": avg_accuracy,
            "overall_feedback": feedback
        }


# Singleton instance
reading_manager = ReadingAssessmentManager()
