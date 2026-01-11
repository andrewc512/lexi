"""Email service for sending notifications via SendGrid."""

from typing import Optional
from app.core.config import settings


async def send_email(
    to: str,
    subject: str,
    body: str,
    html: Optional[str] = None,
) -> bool:
    """
    Send an email via SendGrid.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text body
        html: Optional HTML body
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not settings.SENDGRID_API_KEY:
        print("[EMAIL] SendGrid API key not configured, skipping email")
        return False
    
    if not settings.SENDGRID_FROM_EMAIL:
        print("[EMAIL] SendGrid from email not configured, skipping email")
        return False
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Content
        
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=to,
            subject=subject,
        )
        
        # Add plain text content
        message.add_content(Content("text/plain", body))
        
        # Add HTML content if provided
        if html:
            message.add_content(Content("text/html", html))
        
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"[EMAIL] Sent to {to}, status: {response.status_code}")
        return response.status_code in [200, 201, 202]
        
    except ImportError:
        print("[EMAIL] SendGrid package not installed. Run: pip install sendgrid")
        return False
    except Exception as e:
        print(f"[EMAIL] Error sending email: {e}")
        return False


async def send_interview_invite(
    candidate_email: str,
    candidate_name: str,
    interview_id: str,
    language: str = "English",
) -> bool:
    """
    Send interview invitation email with link.
    
    Args:
        candidate_email: Candidate's email address
        candidate_name: Candidate's name
        interview_id: Interview ID/token for the link
        language: Language the interview will be conducted in
    
    Returns:
        True if email sent successfully
    """
    interview_link = f"{settings.FRONTEND_URL}/interview/{interview_id}"
    
    subject = "You're Invited to Complete a Language Assessment"
    
    # Plain text version
    body = f"""
Hi {candidate_name},

You've been invited to complete an AI-powered language assessment in {language}.

Click the link below to begin:
{interview_link}

What to expect:
- A friendly conversation with our AI assistant, Lexi
- A reading comprehension exercise
- Total duration: approximately 3-5 minutes

This link will expire in 72 hours.

Best regards,
The Lexi Team
    """.strip()
    
    # HTML version (nicer formatting)
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
        .button:hover {{ background: #1d4ed8; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
        .info-box {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">Language Assessment Invitation</h1>
        </div>
        <div class="content">
            <p>Hi <strong>{candidate_name}</strong>,</p>
            
            <p>You've been invited to complete an AI-powered language assessment in <strong>{language}</strong>.</p>
            
            <div style="text-align: center;">
                <a href="{interview_link}" class="button" style="color: white">Start Assessment</a>
            </div>
            
            <div class="info-box">
                <strong>What to expect:</strong>
                <ul>
                    <li>A friendly conversation with our AI assistant, Lexi</li>
                    <li>A reading comprehension exercise</li>
                    <li>Total duration: approximately 3-5 minutes</li>
                </ul>
            </div>
            
            <p style="color: #6b7280; font-size: 14px;">This link will expire in 72 hours.</p>
            
            <p>Best regards,<br><strong>The Lexi Team</strong></p>
        </div>
        <div class="footer">
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p>{interview_link}</p>
        </div>
    </div>
</body>
</html>
    """.strip()
    
    return await send_email(candidate_email, subject, body, html)


async def send_completion_notification(
    recipient_email: str,
    candidate_name: str,
    interview_id: str,
) -> bool:
    """
    Notify that an interview has been completed.
    
    Args:
        recipient_email: Email to send notification to
        candidate_name: Name of the candidate
        interview_id: Interview ID
    
    Returns:
        True if email sent successfully
    """
    dashboard_link = f"{settings.FRONTEND_URL}/dashboard"
    
    subject = f"Assessment Completed: {candidate_name}"
    
    body = f"""
The language assessment for {candidate_name} has been completed.

View the results in your dashboard:
{dashboard_link}

Best regards,
The Lexi Team
    """.strip()
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .button {{ display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">✓ Assessment Completed</h1>
        </div>
        <div class="content">
            <p>The language assessment for <strong>{candidate_name}</strong> has been completed.</p>
            
            <div style="text-align: center;">
                <a href="{dashboard_link}" class="button">View Results</a>
            </div>
            
            <p>Best regards,<br><strong>The Lexi Team</strong></p>
        </div>
    </div>
</body>
</html>
    """.strip()
    
    return await send_email(recipient_email, subject, body, html)
