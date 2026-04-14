from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    content: str
    text: Optional[str] = None