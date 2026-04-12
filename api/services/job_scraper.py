import requests
from bs4 import BeautifulSoup
import random
import concurrent.futures

class JobScraper:
    ROLE_TYPES = {
        "full_time": "F",
        "part_time": "P",
        "contract": "C",
        "temporary": "T",
        "volunteer": "V",
        "internship": "I"
    }

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    ]

    BASE_SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    BASE_JOB_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting"

    def __init__(self, keywords, location, role_type="full_time", limit=5):
        self.keywords = keywords
        self.location = location
        self.role_type = role_type
        self.limit = limit

        self.headers = {
            "User-Agent": random.choice(self.USER_AGENTS)
        }

    # ---------- URL BUILDER ----------
    def build_search_url(self, start=0):
        role_code = self.ROLE_TYPES.get(self.role_type, "F")

        url = (
            f"{self.BASE_SEARCH_URL}"
            f"?keywords={self.keywords}"
            f"&location={self.location}"
            f"&f_JT={role_code}"
            f"&start={start}"
        )

        return url

    # ---------- FETCH JOB LIST ----------
    def fetch_job_list(self, start=0):
        url = self.build_search_url(start)
        response = requests.get(url, headers=self.headers, timeout=10)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch job list: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.find_all("li")

    # ---------- FETCH JOB DETAILS ----------
    def fetch_job_details(self, job_id):
        job_url = f"{self.BASE_JOB_URL}/{job_id}"

        try:
            response = requests.get(job_url, headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            print(f"Timeout fetching job {job_id}, skipping.")
            return None

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        def safe_find(tag, cls):
            el = soup.find(tag, class_=cls)
            return el.text.strip() if el else None

        apply_btn = soup.find("a", {"data-control-name": "jobdetails_topcard_inapply"})
        apply_link = apply_btn["href"] if apply_btn and apply_btn.has_attr("href") else None

        return {
            "job_id": job_id,
            "job_title": safe_find("h2", "top-card-layout__title"),
            "company": safe_find("a", "topcard__org-name-link"),
            "location": safe_find("span", "topcard__flavor--bullet"),
            "description": safe_find("div", "description__text"),
            "apply_link": apply_link,
            "job_url": f"https://www.linkedin.com/jobs/view/{job_id}/"
        }

    # ---------- MAIN PIPELINE ----------
    def scrape_jobs(self, start=0):
        jobs = self.fetch_job_list(start)
        job_ids = []

        for job in jobs:
            if len(job_ids) >= self.limit:
                break

            base_card = job.find("div", class_="base-card")
            if not base_card:
                continue

            job_urn = base_card.get("data-entity-urn")
            if not job_urn:
                continue

            job_ids.append(job_urn.split(":")[3])

        # Fetch all job details in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.fetch_job_details, job_ids))

        return [job for job in results if job]


# --- TEST SCRIPT ---
# if __name__ == "__main__":
#     scraper_with_company = JobScraper(
#         keywords="AI Engineer",
#         location="Singapore",
#         role_type="internship",
#         limit=5
#     )

#     print("\nFetching jobs with company filter...")
#     jobs = scraper_with_company.scrape_jobs()
#     for idx, job in enumerate(jobs, start=1):
#         print(f"\nJob {idx}:")
#         print(f"Title: {job['job_title']}")
#         print(f"Company: {job['company']}")
#         print(f"Description: {job['description'][:100]}...")
#         print(f"Location: {job['location']}")
#         print(f"Apply link: {job['apply_link']}")
#         print(f"Job URL: {job['job_url']}")
