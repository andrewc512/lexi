from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.email import send_interview_invite, send_completion_notification
from app.services.supabase import get_supabase

router = APIRouter()


class SendInviteRequest(BaseModel):
    interview_id: str
    candidate_email: str
    candidate_name: str
    language: Optional[str] = "English"


class SendReportRequest(BaseModel):
    interview_id: str
    recipient_email: str


@router.post("/send-invite")
async def send_invite(request: SendInviteRequest):
    """
    Send interview invitation email to candidate.
    
    This endpoint:
    1. Sends an email with the interview link
    2. Updates the interview status to 'Email sent'
    """
    # Send the email
    success = await send_interview_invite(
        candidate_email=request.candidate_email,
        candidate_name=request.candidate_name,
        interview_id=request.interview_id,
        language=request.language or "English",
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check SendGrid configuration."
        )
    
    # Update interview status in Supabase
    try:
        client = get_supabase()
        if client:
            client.table("interviews").update({
                "status": "Email sent"
            }).eq("id", request.interview_id).execute()
    except Exception as e:
        print(f"Warning: Could not update interview status: {e}")
        # Don't fail the request - email was still sent
    
    return {
        "success": True,
        "message": "Invite sent successfully",
        "interview_id": request.interview_id,
        "recipient": request.candidate_email,
    }


@router.post("/send-report")
async def send_report(request: SendReportRequest):
    """
    Send interview completion report to recipient.
    """
    # Get interview details from Supabase
    candidate_name = "Candidate"
    try:
        client = get_supabase()
        if client:
            result = client.table("interviews").select("name").eq(
                "id", request.interview_id
            ).single().execute()
            if result.data:
                candidate_name = result.data.get("name", "Candidate")
    except Exception as e:
        print(f"Warning: Could not fetch interview details: {e}")
    
    success = await send_completion_notification(
        recipient_email=request.recipient_email,
        candidate_name=candidate_name,
        interview_id=request.interview_id,
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send report email."
        )
    
    return {
        "success": True,
        "message": "Report sent successfully",
        "interview_id": request.interview_id,
        "recipient": request.recipient_email,
    }
