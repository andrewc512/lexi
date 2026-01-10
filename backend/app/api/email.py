from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SendInviteRequest(BaseModel):
    interview_id: str
    candidate_email: str
    candidate_name: str


class SendReportRequest(BaseModel):
    interview_id: str
    recipient_email: str


@router.post("/send-invite")
async def send_invite(request: SendInviteRequest):
    # TODO: Send actual email via email service
    return {
        "message": "Invite sent",
        "interview_id": request.interview_id,
        "recipient": request.candidate_email,
    }


@router.post("/send-report")
async def send_report(request: SendReportRequest):
    # TODO: Generate PDF report
    # TODO: Send actual email via email service
    return {
        "message": "Report sent",
        "interview_id": request.interview_id,
        "recipient": request.recipient_email,
    }
