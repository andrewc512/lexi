"""Evaluation service for scoring interviews."""

from typing import List, Dict
from app.models.evaluation import Evaluation, EvaluationCriteria


async def evaluate_interview(
    interview_id: str,
    answers: List[Dict],
) -> Evaluation:
    """
    Evaluate an entire interview.
    
    TODO: Implement comprehensive evaluation using LLM
    """
    # Stub evaluation
    criteria = [
        EvaluationCriteria(
            name="Communication",
            score=8,
            max_score=10,
            feedback="Clear and articulate responses.",
        ),
        EvaluationCriteria(
            name="Problem Solving",
            score=7,
            max_score=10,
            feedback="Demonstrated logical thinking.",
        ),
        EvaluationCriteria(
            name="Experience Relevance",
            score=8,
            max_score=10,
            feedback="Relevant examples provided.",
        ),
    ]

    overall_score = sum(c.score for c in criteria) / sum(c.max_score for c in criteria) * 100

    return Evaluation(
        id="eval_stub",
        interview_id=interview_id,
        overall_score=int(overall_score),
        summary="Overall strong candidate with good communication skills.",
        criteria=criteria,
        created_at="2024-01-15T12:00:00Z",
    )


async def score_answer(
    question: str,
    answer: str,
    criteria: List[str],
) -> Dict:
    """
    Score a single answer against criteria.
    
    TODO: Implement using LLM
    """
    return {
        "score": 7,
        "max_score": 10,
        "breakdown": {criterion: 7 for criterion in criteria},
    }
