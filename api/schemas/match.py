from typing import Optional

from openai import BaseModel

class MatchRequest(BaseModel):
    job_desc: str
    resume: str

class MatchResponse(BaseModel):
    overall_score: int
    keyword_score: float
    embedding_score: float
    llm_judge_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    bonus_skills: list[str]
    strengths: list[str]
    gaps: list[str]
    recommendation: str
    summary: str
