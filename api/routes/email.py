from fastapi import APIRouter, HTTPException
from services.send_email import EmailService  
from schemas.email import EmailRequest

router = APIRouter(prefix="/email", tags=["email"])
mailer = EmailService()

@router.post("/")
def send_email(payload: EmailRequest):
    try:
        result = mailer.send_mail(
            to=payload.to,
            subject=payload.subject,
            content=payload.content
        )
        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )