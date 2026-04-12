# routes/jobs.py
from fastapi import APIRouter
from services.job_scraper import JobScraper

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

@router.get("/")
def get_jobs(keywords: str, location: str, role: str = "full_time"):
    print(f"\n Searching for jobs with keywords='{keywords}', location='{location}', role='{role}")
    scraper = JobScraper(keywords, location, role_type=role)
    jobs = scraper.scrape_jobs()
    return {"jobs": jobs}