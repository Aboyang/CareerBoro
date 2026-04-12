# **CareerBoro API Documentation**

## **Base URL**

```
http://localhost:8000
```

---

## **1. Research Endpoints**

### **1.1 Search Webpages**

* **Method:** `POST`
* **Endpoint:** `/research/search`
* **Description:** Search the web for a given query.

**Request Body:**

```json
{
  "query": "string",
  "limit": 5
}
```

* `query` *(string)*: The search query.
* `limit` *(integer, optional)*: Maximum number of search results (default 5).

**Response (200 OK):**

```text
"string"  // JSON string containing search results
```

---

### **1.2 Read Webpage**

* **Method:** `POST`
* **Endpoint:** `/research/read`
* **Description:** Fetch and read content from a webpage.

**Request Body:**

```json
{
  "url": "string"
}
```

**Response (200 OK):**

```text
"string"  // The text content of the webpage
```

---

### **1.3 Summarise Content**

* **Method:** `POST`
* **Endpoint:** `/research/summarise`
* **Description:** Summarise the input content.

**Request Body:**

```json
{
  "content": "string"
}
```

**Response (200 OK):**

```text
"string"  // Summarised version of the content
```

---

### **1.4 Full Research**

* **Method:** `POST`
* **Endpoint:** `/research/`
* **Description:** Perform a full research workflow combining search, read, and summarisation.

**Request Body:**

```json
{
  "query": "string"
}
```

**Response (200 OK):**

```text
"string"  // Full research output
```

---

## **2. Jobs Endpoints**

### **2.1 Get Jobs**

* **Method:** `GET`
* **Endpoint:** `/jobs/`
* **Description:** Retrieve a list of jobs filtered by keywords, location, and role.

**Query Parameters:**

* `keywords` *(string, required)*: Job keywords to search.
* `location` *(string, required)*: Job location.
* `role` *(string, optional)*: Job type (default: `"full_time"`).

**Response (200 OK):**

```text
"string"  // List of job postings in JSON/text format
```

---

## **3. JD-Resume Match Endpoint**

### **3.1 Match Job Resume**

* **Method:** `POST`
* **Endpoint:** `/match/`
* **Description:** Compute a hybrid match between a job description and a candidate resume, including keyword, embedding, and LLM-based scoring.

**Request Body:**

```json
{
  "job_desc": "string",
  "resume": "string",
  "additionalProp1": {}
}
```

**Response (200 OK):**

```json
{
  "overall_score": 0,
  "keyword_score": 0,
  "embedding_score": 0,
  "llm_judge_score": 0,
  "matched_skills": ["string"],
  "missing_skills": ["string"],
  "bonus_skills": ["string"],
  "strengths": ["string"],
  "gaps": ["string"],
  "recommendation": "string",
  "summary": "string",
  "additionalProp1": {}
}
```

**Fields:**

* `overall_score`: Total match score.
* `keyword_score`: Score based on keyword matching.
* `embedding_score`: Semantic similarity score.
* `llm_judge_score`: LLM evaluation score.
* `matched_skills`: Skills found in both resume and job description.
* `missing_skills`: Skills required but not in the resume.
* `bonus_skills`: Extra skills in the resume.
* `strengths`: Candidate strengths.
* `gaps`: Candidate skill gaps.
* `recommendation`: Suggested action.
* `summary`: Brief summary of matching results.

---

## **4. Error Responses**

For all endpoints:

**HTTP 422 – Validation Error**

```json
{
  "detail": [
    {
      "loc": ["string", 0],
      "msg": "string",
      "type": "string",
      "input": "string",
      "ctx": {}
    }
  ]
}
```

---