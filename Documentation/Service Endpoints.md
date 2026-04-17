# 📘 API Documentation

The following API endpoints represent the various services that the agent can execute through tool invocation.

* `POST /email/`
  → Send an email

* `GET /jobs/`
  → Scrape jobs based on keywords, location, and role

* `POST /jobs/save`
  → Save a job to the database

* `POST /match/`
  → Match job description with resume and generate insights

* `POST /research/search`
  → Search for relevant webpages

* `POST /research/read`
  → Extract content from a webpage

* `POST /research/summarise`
  → Summarise webpage content

* `POST /research/`
  → Full research pipeline (search → read → summarise)

---

## Base URL

```
/api (or wherever your FastAPI app is mounted)
```

---

# Email Service

## `POST /email/`

Send an email.

### Request Body

```json
{
  "to": "recipient@example.com",
  "subject": "Subject here",
  "content": "Email body content"
}
```

### Response

```json
{
  "success": true,
  "data": "..." 
}
```

### Errors

`500 Internal Server Error` – Failed to send email

---

# Job Service

## `GET /jobs/`

Scrape jobs based on filters.

### Query Parameters

| Parameter | Type   | Required | Description                        |
| --------- | ------ | -------- | ---------------------------------- |
| keywords  | string | ✅        | Search keywords                    |
| location  | string | ✅        | Job location                       |
| role      | string | ✅        | Role type (e.g. intern, full-time) |
| limit     | int    | ✅        | Number of jobs to fetch            |

### Example

```
GET /jobs/?keywords=python&location=singapore&role=intern&limit=10
```

### Response

```json
{
  "jobs": [
    {
      "role": "...",
      "company": "...",
      "description": "...",
      "apply_link": "..."
    }
  ]
}
```

---

## `POST /jobs/save`

Save a job into the database.

### Request Body

```json
{
  "role": "Software Engineer Intern",
  "company": "Google",
  "job_desc": "...",
  "apply_link": "...",
  "research": "...",
  "webpages_read": ["url1", "url2"]
}
```

### Response

```json
{
  "message": "saved",
  "job_id": 123,
  "response": "..."
}
```

---

# 🤖 Job Description ↔ Resume Matching

## `POST /match/`

Compute similarity between a job description and a resume.

### Request Body

```json
{
  "job_desc": "Job description text...",
  "resume": "Resume text..."
}
```

### Response

```json
{
  "overall_score": 0.85,
  "keyword_score": 0.8,
  "embedding_score": 0.87,
  "llm_judge_score": 0.88,
  "matched_skills": ["Python", "SQL"],
  "missing_skills": ["Docker"],
  "bonus_skills": ["AWS"],
  "strengths": ["Strong backend experience"],
  "gaps": ["Lacks cloud exposure"],
  "recommendation": "Improve cloud skills",
  "summary": "Good match overall"
}
```

---

# 🔍 Research Service

## `POST /research/search`

Search for relevant webpages.

### Request Body

```json
{
  "query": "AI internships Singapore",
  "limit": 5
}
```

### Response

```json
{
  "urls": ["url1", "url2"]
}
```

---

## `POST /research/read`

Extract content from a webpage.

### Request Body

```json
{
  "url": "https://example.com",
  "char_limit": 2000
}
```

### Response

```json
{
  "content": "Extracted text..."
}
```

---

## `POST /research/summarise`

Summarise webpage content.

### Request Body

```json
{
  "content": "Long webpage text..."
}
```

### Response

```json
{
  "summary": "Short summary..."
}
```

---

## `POST /research/` (Full Pipeline)

End-to-end research workflow:

1. Search webpages
2. Read content
3. Summarise results

### Request Body

```json
{
  "query": "AI startups Singapore",
  "limit": 3,
  "char_limit": 2000
}
```

### Response

```json
{
  "query": "AI startups Singapore",
  "results": [
    {
      "url": "https://example.com",
      "summary": "..."
    }
  ]
}
```