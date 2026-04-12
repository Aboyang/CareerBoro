# ISSUE
# Consider whether we want full research flow or bit by bit research
# Consider whether we want LangGraph structure

# tools.py
import requests
from langchain.tools import tool

BASE_URL = "http://localhost:8001"

# ------------------------
# Research Tools
# ------------------------

@tool
def browse_internet(query: str, limit: int = 5) -> str:
    """Search webpages using the research endpoint."""
    url = f"{BASE_URL}/research/search"
    payload = {"query": query, "limit": limit}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.text

@tool
def read_webpage(url_to_read: str) -> str:
    """Read content from a webpage."""
    url = f"{BASE_URL}/research/read"
    payload = {"url": url_to_read}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.text

@tool
def summarise(content: str) -> str:
    """Summarise given content."""
    url = f"{BASE_URL}/research/summarise"
    payload = {"content": content}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.text

# ------------------------
# Jobs Tools
# ------------------------

@tool
def fetch_jobs(keywords: str, location: str, role: str, limit: int = 5) -> str:
    """Get jobs from the job endpoint."""
    url = f"{BASE_URL}/jobs/"
    params = {"keywords": keywords, "location": location, "role": role, "limit": limit}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.text

@tool
def save_job(role: str, company: str, job_desc: str, apply_link: str, research: str, webpages_read: list) -> str:
    """
    Save a job to the database.
    """

    url = f"{BASE_URL}/jobs/save"

    payload = {
        "role": role,
        "company": company,
        "job_desc": job_desc,
        "apply_link": apply_link,
        "research": research,
        "webpages_read": webpages_read
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.text

# ------------------------
# JD-Resume Match Tool
# ------------------------

@tool
def match_job_resume(job_desc: str, resume: str, additional: dict = {}) -> dict:
    """Compute a hybrid match between a job description and a candidate resume."""
    url = f"{BASE_URL}/match/"
    payload = {"job_desc": job_desc, "resume": resume, "additionalProp1": additional}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()