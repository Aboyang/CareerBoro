from pydantic import BaseModel
from typing import Any

class QuestionRequest(BaseModel):
    role: str
    company: str
    job_desc: str
    resume_context: Any