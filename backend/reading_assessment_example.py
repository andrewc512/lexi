#!/usr/bin/env python3
"""
Example usage of the Reading Assessment system.

This script demonstrates how the reading assessment works
independently of the WebSocket integration.
"""

import asyncio
import time
from app.services.reading_assessment import reading_manager


async def example_full_reading_session():
    """
    Example: Complete reading assessment session.
    """
    print("=" * 60)
    print("READING ASSESSMENT EXAMPLE")
    print("=" * 60)

    # 1. Check if it's time to transition to reading phase
    print("\n1. TIMING CHECK")
    print("-" * 60)

    interview_start = time.time() - 181  # Simulate 3+ minutes elapsed
    current_time = time.time()

    should_transition = reading_manager.should_transition_to_reading(
        interview_start,
        current_time
    )

    print(f"Interview started at: {interview_start}")
    print(f"Current time: {current_time}")
    print(f"Time elapsed: {(current_time - interview_start):.1f} seconds")
    print(f"Should transition to reading? {should_transition}")

    # 2. Get transition message
    print("\n2. TRANSITION MESSAGE")
    print("-" * 60)

    transition_msg = reading_manager.get_transition_message("Spanish")
    print(f"AI says: '{transition_msg}'")

    # 3. Generate a reading passage
    print("\n3. GENERATE READING PASSAGE")
    print("-" * 60)

    passage_data = await reading_manager.generate_reading_passage(
        target_language="Spanish",
        difficulty_level=3
    )

    print(f"Passage: {passage_data['passage']}")
    print(f"Topic: {passage_data['topic']}")
    print(f"Difficulty: {passage_data['difficulty']}/10")

    # 4. Simulate user translation
    print("\n4. USER TRANSLATION")
    print("-" * 60)

    # User's English translation (simulated)
    user_translation = "Yesterday I went to the market. I bought apples and bread."
    print(f"User translates to English: '{user_translation}'")

    # 5. Evaluate the translation
    print("\n5. EVALUATE TRANSLATION")
    print("-" * 60)

    evaluation = await reading_manager.evaluate_reading_translation(
        original_passage=passage_data["passage"],
        user_translation=user_translation,
        target_language="Spanish",
        difficulty_level=3
    )

    print(f"📊 Scores:")
    print(f"  - Comprehension: {evaluation['comprehension_score']:.1f}%")
    print(f"  - Accuracy: {evaluation['accuracy_score']:.1f}%")
    print(f"  - Grammar: {evaluation['grammar_score']:.1f}%")
    print(f"\n💬 Feedback: {evaluation['feedback']}")

    if evaluation.get('errors'):
        print(f"\n⚠️  Errors:")
        for error in evaluation['errors']:
            print(f"  - {error}")

    if evaluation.get('strengths'):
        print(f"\n✅ Strengths:")
        for strength in evaluation['strengths']:
            print(f"  - {strength}")

    print(f"\n💡 Correct Translation: {evaluation.get('correct_translation', 'N/A')}")

    # 6. Generate multiple passages with difficulty adaptation
    print("\n6. DIFFICULTY ADAPTATION")
    print("-" * 60)

    reading_evaluations = [evaluation]
    current_difficulty = 3
    previous_passages = [passage_data["passage"]]

    # Simulate 3 more reading exercises
    for i in range(3):
        # Adjust difficulty based on previous score
        last_score = reading_evaluations[-1]['accuracy_score']

        if last_score > 85:
            current_difficulty = min(10, current_difficulty + 1)
            print(f"\n✅ Good score ({last_score:.0f}%) → Increasing difficulty to {current_difficulty}")
        elif last_score < 60:
            current_difficulty = max(1, current_difficulty - 1)
            print(f"\n⚠️  Low score ({last_score:.0f}%) → Decreasing difficulty to {current_difficulty}")
        else:
            print(f"\n➡️  Average score ({last_score:.0f}%) → Keeping difficulty at {current_difficulty}")

        # Generate next passage
        next_passage = await reading_manager.generate_reading_passage(
            target_language="Spanish",
            difficulty_level=current_difficulty,
            previous_passages=previous_passages
        )

        previous_passages.append(next_passage["passage"])

        print(f"   New passage (diff {current_difficulty}): {next_passage['passage'][:50]}...")

        # Simulate evaluation (using mock data for brevity)
        mock_evaluation = {
            'comprehension_score': 70 + (i * 5),  # Gradually improving
            'accuracy_score': 75 + (i * 5),
            'grammar_score': 72 + (i * 5),
            'feedback': f"Exercise {i+2} feedback",
            'errors': [],
            'strengths': [],
            'correct_translation': 'Mock translation'
        }

        reading_evaluations.append(mock_evaluation)

    # 7. Calculate final proficiency
    print("\n7. FINAL READING PROFICIENCY")
    print("-" * 60)

    proficiency = reading_manager.calculate_reading_proficiency(reading_evaluations)

    print(f"📚 Reading Level: {proficiency['reading_level']} (CEFR)")
    print(f"📊 Comprehension Score: {proficiency['comprehension_score']:.1f}%")
    print(f"📊 Accuracy Score: {proficiency['accuracy_score']:.1f}%")
    print(f"💬 Overall Feedback: {proficiency['overall_feedback']}")

    print("\n" + "=" * 60)
    print("READING ASSESSMENT COMPLETE")
    print("=" * 60)


async def example_timing_check():
    """
    Example: Check if it's time to transition to reading phase.
    """
    print("\n" + "=" * 60)
    print("TIMING CHECK EXAMPLES")
    print("=" * 60)

    now = time.time()

    # Test case 1: Just started (0 seconds)
    start1 = now
    result1 = reading_manager.should_transition_to_reading(start1, now)
    print(f"\nCase 1 - Just started (0s elapsed): {result1}")
    print(f"  Expected: False, Got: {result1}")

    # Test case 2: 2 minutes elapsed (not yet)
    start2 = now - 120
    result2 = reading_manager.should_transition_to_reading(start2, now)
    print(f"\nCase 2 - 2 minutes elapsed: {result2}")
    print(f"  Expected: False, Got: {result2}")

    # Test case 3: Exactly 3 minutes (180s)
    start3 = now - 180
    result3 = reading_manager.should_transition_to_reading(start3, now)
    print(f"\nCase 3 - Exactly 3 minutes (180s): {result3}")
    print(f"  Expected: True, Got: {result3}")

    # Test case 4: 5 minutes elapsed
    start4 = now - 300
    result4 = reading_manager.should_transition_to_reading(start4, now)
    print(f"\nCase 4 - 5 minutes elapsed: {result4}")
    print(f"  Expected: True, Got: {result4}")


async def main():
    """Run all examples."""

    # Example 1: Timing checks
    await example_timing_check()

    # Example 2: Full reading session
    await example_full_reading_session()


if __name__ == "__main__":
    print("\n" + "🎓 " * 20)
    print("READING ASSESSMENT SYSTEM - EXAMPLES")
    print("🎓 " * 20)

    asyncio.run(main())

    print("\n" + "✅ " * 20)
    print("All examples completed successfully!")
    print("✅ " * 20 + "\n")
