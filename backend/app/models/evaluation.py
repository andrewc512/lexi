from pydantic import BaseModel
from typing import List


class EvaluationCriteria(BaseModel):
    name: str
    score: int
    max_score: int
    feedback: str


class Evaluation(BaseModel):
    id: str
    interview_id: str
    overall_score: int
    summary: str
    criteria: List[EvaluationCriteria]
    created_at: str


class AnswerEvaluation(BaseModel):
    answer_id: str
    question: str
    score: int
    max_score: int
    feedback: str
    strengths: List[str]
    improvements: List[str]
