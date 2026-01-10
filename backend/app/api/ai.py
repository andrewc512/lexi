from fastapi import APIRouter

router = APIRouter()

STUB_QUESTIONS = [
    "Tell me about yourself and your background.",
    "What interests you most about this role?",
    "Describe a challenging project you've worked on.",
    "How do you handle tight deadlines and pressure?",
    "Where do you see yourself in five years?",
]


@router.get("/question")
async def get_question(number: int = 0):
    # TODO: Generate dynamic questions using LLM
    question = STUB_QUESTIONS[number % len(STUB_QUESTIONS)]
    return {"question": question, "number": number}


@router.post("/evaluate")
async def evaluate_answer(interview_id: str, answer_text: str):
    # TODO: Use LLM to evaluate the answer
    return {
        "interview_id": interview_id,
        "score": 8,
        "feedback": "Good response with clear examples.",
    }


@router.post("/generate-followup")
async def generate_followup(interview_id: str, previous_answer: str):
    # TODO: Use LLM to generate follow-up question
    return {
        "question": "Can you elaborate more on that experience?",
        "context": "follow-up",
    }
