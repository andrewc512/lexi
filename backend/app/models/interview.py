from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class InterviewStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class InterviewCreate(BaseModel):
    name: str
    email: str


class Interview(BaseModel):
    id: str
    token: str
    candidate_name: str
    candidate_email: str
    status: InterviewStatus
    created_at: str
    completed_at: Optional[str] = None


class Answer(BaseModel):
    id: str
    interview_id: str
    question_number: int
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    submitted_at: str


class InterviewSession(BaseModel):
    interview_id: str
    current_question: int
    answers: List[Answer]
    started_at: str
