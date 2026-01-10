"""LLM service for AI-powered features."""

from typing import List, Optional


async def generate_question(
    context: Optional[str] = None,
    previous_questions: Optional[List[str]] = None,
) -> str:
    """
    Generate an interview question.
    
    TODO: Implement using OpenAI/Anthropic API
    """
    return "Tell me about a time when you overcame a significant challenge."


async def generate_followup(
    previous_answer: str,
    question_context: Optional[str] = None,
) -> str:
    """
    Generate a follow-up question based on the candidate's answer.
    
    TODO: Implement using LLM
    """
    return "Can you provide more details about that experience?"


async def analyze_response(
    question: str,
    answer: str,
) -> dict:
    """
    Analyze a candidate's response.
    
    TODO: Implement using LLM
    """
    return {
        "relevance": 8,
        "clarity": 7,
        "depth": 6,
        "feedback": "Good response with room for more specific examples.",
    }
