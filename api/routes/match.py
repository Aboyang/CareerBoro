# routes/match.py
from fastapi import APIRouter
from typing import Optional
from services.job_desc_resume_matcher import JobDescResumeMatch, MatchResult
from schemas.match import MatchRequest, MatchResponse

router = APIRouter(prefix="/match", tags=["JD-Resume Match"])

@router.post("/", response_model=MatchResponse)
def match_job_resume(payload: MatchRequest):
    """
    Compute a hybrid match between a job description and a candidate resume.
    """
    matcher = JobDescResumeMatch(
        job_desc=payload.job_desc,
        resume_string=payload.resume
    )

    result: MatchResult = matcher.compute_match()

    return MatchResponse(
        overall_score=result.overall_score,
        keyword_score=result.keyword_score,
        embedding_score=result.embedding_score,
        llm_judge_score=result.llm_judge_score,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        bonus_skills=result.bonus_skills,
        strengths=result.strengths,
        gaps=result.gaps,
        recommendation=result.recommendation,
        summary=result.summary
    )