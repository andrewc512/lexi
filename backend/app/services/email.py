"""Email service for sending notifications."""

from typing import Optional


async def send_email(
    to: str,
    subject: str,
    body: str,
    html: Optional[str] = None,
) -> bool:
    """
    Send an email.
    
    TODO: Implement using:
    - SendGrid
    - AWS SES
    - SMTP
    """
    print(f"[EMAIL STUB] To: {to}, Subject: {subject}")
    return True


async def send_interview_invite(
    candidate_email: str,
    candidate_name: str,
    interview_link: str,
) -> bool:
    """
    Send interview invitation email.
    
    TODO: Use email template
    """
    subject = "You're Invited to Complete an Interview"
    body = f"""
    Hi {candidate_name},
    
    You've been invited to complete an AI-powered interview.
    
    Click the link below to begin:
    {interview_link}
    
    This link will expire in 72 hours.
    
    Best regards,
    The Lexi Team
    """
    return await send_email(candidate_email, subject, body)


async def send_completion_notification(
    recipient_email: str,
    candidate_name: str,
    interview_id: str,
) -> bool:
    """
    Notify that an interview has been completed.
    
    TODO: Implement notification
    """
    subject = f"Interview Completed: {candidate_name}"
    body = f"The interview for {candidate_name} has been completed. View the report in your dashboard."
    return await send_email(recipient_email, subject, body)
