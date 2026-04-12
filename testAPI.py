# test_research_api.py

import requests
import json

BASE_URL = "http://localhost:8000/research"
BASE_URL_JOBS = "http://localhost:8000/jobs"

def test_search():
    payload = {"query": "OCBC digital transformation strategy", "limit": 3}
    response = requests.post(f"{BASE_URL}/search", json=payload)
    print("\n--- SEARCH RESULT ---")
    print(json.dumps(response.json(), indent=2))

def test_read():
    payload = {"url": "https://www.theasianbanker.com/updates-and-articles/ocbc-advances-digital-banking-through-enhanced-architecture-and-embedded-integration", "char_limit": 500}
    response = requests.post(f"{BASE_URL}/read", json=payload)
    print("\n--- READ RESULT ---")
    print(json.dumps(response.json(), indent=2))

def test_summarise():
    payload = {"content": "OCBC operates one of the largest small and medium enterprise (SME) banking franchises in Singapore, representing nearly half of all SMEs nationwide. Across Singapore, Malaysia, Indonesia, Hong Kong, China and Macau, the bank now delivers business banking under a One Group digital model, supported by shared infrastructure that enables scale, consistency and faster deployment across markets. Carmen Chan, deputy head of global transaction banking, OCBC, said the evolution of Velocity and the OCBC B"}
    response = requests.post(f"{BASE_URL}/summarise", json=payload)
    print("\n--- SUMMARISE RESULT ---")
    print(json.dumps(response.json(), indent=2))

def job_search():
    params = {
        "keywords": "data analyst",
        "location": "Singapore",
        "role": "full_time"
    }
    response = requests.get(BASE_URL_JOBS, params=params)
    print(response.status_code)
    print("\n--- JOB SEARCH RESULT ---")
    print(json.dumps(response.json(), indent=2))

def test_match():
    payload = {
        "job_desc": "We are seeking a skilled Data Analyst to join our team. The ideal candidate will have experience in data analysis, proficiency in SQL and Python, and the ability to visualize data using tools like Tableau or Power BI. Responsibilities include collecting and analyzing data, creating reports, and providing insights to support business decisions.",
        "resume": "Some one with experience in doom scrolling and smelling armpits. Proficient in yapping."
    }
    response = requests.post("http://localhost:8000/match/", json=payload)
    print("\n--- MATCH RESULT ---")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    # test_search()
    # test_read()
    # test_summarise()
    test_match()

