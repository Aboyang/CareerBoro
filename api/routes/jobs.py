from fastapi import APIRouter
from services.job_scraper import JobScraper
from services.job_db import JobDB
from schemas.job import JobRequest

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

db = JobDB()


@router.get("/")
def get_jobs(keywords: str, location: str, role: str, limit: int):
    scraper = JobScraper(keywords, location, role_type=role, limit=limit)
    jobs = scraper.scrape_jobs()
    return {"jobs": jobs}


@router.post("/save")
def save_jobs(job: JobRequest):

    response, job_id = db.save_job_to_db(
        job.role,
        job.company,
        job.job_desc,
        job.apply_link,
        job.research,
        job.webpages_read
    )

    return {
        "message": "saved",
        "job_id": job_id,
        "response": response
    }
