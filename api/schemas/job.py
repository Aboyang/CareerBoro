from pydantic import BaseModel
from typing import List

# class WebPage(BaseModel):
#     url: str

class JobRequest(BaseModel):
    role: str
    company: str
    job_desc: str
    apply_link: str
    research: str = ""
    webpages_read: list = []