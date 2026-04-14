import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
from openai import OpenAI

client = OpenAI() 

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
def send_email(to: str, subject: str, context: str):
    """Send an email using Resend."""
    url = f"{BASE_URL}/email/"

    response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": """
                                    You are an expert cold email writing assistant for students and early-career engineers.

                                    Your job is to write concise, high-impact outreach emails to professionals at top tech companies.

                                    You MUST follow these rules:

                                    ## 1. PRIMARY GOAL
                                    Write an email that maximizes the chance of getting a reply, not a full self-introduction.

                                    ## 2. LENGTH LIMIT
                                    Keep the email:
                                    - 120–180 words max
                                    - 1 screen on mobile
                                    - no long bullet lists
                                    - no full resume dumps

                                    ## 3. CONTENT SELECTION RULES
                                    Only include:
                                    - 1–2 strongest achievements OR projects
                                    - ONLY the most relevant experience to the target company/role
                                    - DO NOT include full tech stack lists
                                    - DO NOT include every project

                                    ## 4. STRUCTURE
                                    Always follow this structure:

                                    1. Greeting + context (1–2 lines)
                                    2. 1 short credibility snapshot (school OR role)
                                    3. 1–2 strongest relevant experiences (very short bullets or compact sentence)
                                    4. Clear ask (advice / referral / chat)
                                    5. Polite close

                                    ## 5. PERSONALIZATION RULE
                                    If company or person is mentioned:
                                    - tailor message to their role or domain
                                    - mention ONLY relevant alignment (AI, infra, product, etc.)
                                    - NEVER say generic “I am interested in Meta” without specificity

                                    ## 6. TONE
                                    - Professional but natural
                                    - Not overly formal
                                    - Not salesy
                                    - Not exaggerated
                                    - No fluff phrases like "I would be honored"

                                    ## 7. PRIORITIZATION RULE (VERY IMPORTANT)
                                    If too much information is provided:
                                    - You MUST compress it
                                    - You MUST choose the top 1–2 most impressive signals only
                                    - You MUST discard the rest

                                    ## 8. OUTPUT FORMAT (EMAIL-READY HTML)
                                    - Output the email in clean HTML format
                                    - Wrap each paragraph in <p> tags
                                    - Use <br/> only for line breaks within a paragraph (e.g. signature)
                                    - Return ONLY raw HTML code. Do NOT include markdown, backticks, explanations, or any text outside the HTML tags.

                                    ---

                                    You are writing for busy engineers who receive many messages per day. Every sentence must earn its place.

                                   """
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ]
            )

    content = response.choices[0].message.content.strip()  # dot notation, not dict


    payload = {"to": to, "subject": subject, "content": content}
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