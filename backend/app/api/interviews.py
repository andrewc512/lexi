from fastapi import APIRouter, UploadFile, File
from typing import List

from app.models.interview import Interview, InterviewCreate, Answer
from app.models.evaluation import Evaluation

router = APIRouter()


@router.get("", response_model=List[Interview])
async def list_interviews():
    # TODO: Fetch from Supabase
    return [
        {
            "id": "int_001",
            "token": "abc123",
            "candidate_name": "John Doe",
            "candidate_email": "john@example.com",
            "status": "completed",
            "created_at": "2024-01-15T10:00:00Z",
            "completed_at": "2024-01-15T10:45:00Z",
        },
        {
            "id": "int_002",
            "token": "def456",
            "candidate_name": "Jane Smith",
            "candidate_email": "jane@example.com",
            "status": "pending",
            "created_at": "2024-01-16T14:00:00Z",
            "completed_at": None,
        },
    ]


@router.post("", response_model=Interview)
async def create_interview(data: InterviewCreate):
    # TODO: Create in Supabase
    # TODO: Generate unique token
    # TODO: Send invitation email
    return {
        "id": "int_003",
        "token": "xyz789",
        "candidate_name": data.name,
        "candidate_email": data.email,
        "status": "pending",
        "created_at": "2024-01-17T09:00:00Z",
        "completed_at": None,
    }


@router.get("/{interview_id}", response_model=Interview)
async def get_interview(interview_id: str):
    # TODO: Fetch from Supabase
    return {
        "id": interview_id,
        "token": "abc123",
        "candidate_name": "John Doe",
        "candidate_email": "john@example.com",
        "status": "in_progress",
        "created_at": "2024-01-15T10:00:00Z",
        "completed_at": None,
    }


@router.get("/{interview_id}/evaluation", response_model=Evaluation)
async def get_evaluation(interview_id: str):
    # TODO: Fetch from Supabase
    return {
        "id": "eval_001",
        "interview_id": interview_id,
        "overall_score": 85,
        "summary": "Strong candidate with excellent communication skills.",
        "criteria": [
            {
                "name": "Communication",
                "score": 9,
                "max_score": 10,
                "feedback": "Clear and articulate responses.",
            },
            {
                "name": "Technical Knowledge",
                "score": 8,
                "max_score": 10,
                "feedback": "Good understanding of core concepts.",
            },
        ],
        "created_at": "2024-01-15T11:00:00Z",
    }


@router.post("/{interview_id}/answer")
async def submit_answer(interview_id: str, audio: UploadFile = File(...)):
    # TODO: Upload audio to storage
    # TODO: Transcribe audio
    # TODO: Store answer in Supabase
    return {
        "message": "Answer submitted",
        "interview_id": interview_id,
        "filename": audio.filename,
    }
