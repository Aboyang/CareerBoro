# Agent Architecture Documentation

## Overview

This agent is a modular, tool-augmented system built using **LangChain**, designed to support workflows such as:

* Job search and tracking
* Resume–job matching
* Research (web browsing + summarization)
* Automated outreach (email generation + sending)

The architecture separates **model**, **tools**, and **behavior (system prompt)** for flexibility and scalability.

---

## Project Structure

```
backend/agent/
│
├── model.py          # Defines the LLM used by the agent
├── tools.py          # Defines all callable tools (APIs/functions)
├── system_prompt.py  # Defines agent behavior and instructions
├── agent.py          # Initializes and runs the agent
```

---

## 1. Model Layer (`model.py`)

Defines the core language model powering the agent.

* Uses `init_chat_model` from LangChain
* Configured with:

  * **Model**: `gpt-5.1`
  * **Temperature**: `0` (deterministic outputs)

### Purpose

* Handles reasoning
* Decides when to call tools
* Generates final responses

---

## 2. Tools Layer (`tools.py`)

Defines all external capabilities exposed to the agent via LangChain `@tool`.

### Research Tools

| Tool                            | Description                             |
| ------------------------------- | --------------------------------------- |
| `browse_internet(query, limit)` | Searches the web via `/research/search` |
| `read_webpage(url)`             | Extracts webpage content                |
| `summarise(content)`            | Summarises raw text                     |

---

### Job Tools

| Tool                                          | Description                              |
| --------------------------------------------- | ---------------------------------------- |
| `fetch_jobs(keywords, location, role, limit)` | Retrieves job listings                   |
| `save_job(...)`                               | Stores job data + research into database |

---

### Matching Tool

| Tool                                             | Description                       |
| ------------------------------------------------ | --------------------------------- |
| `match_job_resume(job_desc, resume, additional)` | Computes job–resume compatibility |

---

### Email Tool

| Tool                               | Description                            |
| ---------------------------------- | -------------------------------------- |
| `send_email(to, subject, context)` | Generates + sends cold outreach emails |

#### Key Details:

* Uses **OpenAI API** (`gpt-4o-mini`) for email generation
* Applies a **strict system prompt** to:

  * Keep emails concise (120–180 words)
  * Prioritize high-impact content
  * Output clean HTML
* Sends email via backend `/email/` endpoint

---

## 3. System Prompt (`system_prompt.py`)

Defines the **agent’s behavior and decision-making style**.

### Responsibilities:

* Guides tool usage
* Controls tone and reasoning
* Ensures structured workflows (e.g., research → summarize → act)

### Importance:

This is the **“brain policy layer”** — it determines:

* When to call tools
* How to prioritize actions
* How responses are structured

---

## 4. Agent Initialization (`agent.py`)

The agent is constructed using:

* Model
* Tools
* System prompt

```python
self.agent = create_agent(
    model=model,
    tools=self.tools,
    system_prompt=SYSTEM_PROMPT
)
```

### Registered Tools:

```python
[
  browse_internet,
  read_webpage,
  match_job_resume,
  fetch_jobs,
  save_job,
  send_email
]
```

---

## 5. Execution Methods

### `invoke(content: str)`

* Synchronous execution
* Returns full response at once

```python
agent.invoke("Find SWE internships in Singapore")
```

---

### `astream(content: str)`

* Asynchronous streaming execution
* Emits real-time events:

#### Event Types:

| Event        | Output                    |
| ------------ | ------------------------- |
| Tool Start   | ⚙️ Calling tool...        |
| Tool End     | ✅ Tool done               |
| Model Stream | Incremental response text |

#### Special Behavior:

* Emits `"---FINAL---"` as a sentinel when final response begins
* Filters out tool call chunks from model stream

---

## End-to-End Flow

1. User sends query
2. Agent (LLM) interprets intent
3. Decides whether to:

   * Call tools (API endpoints)
   * Or respond directly
4. Tool results are fed back into the model
5. Final response is generated or streamed

---

## Backend Dependencies

The agent relies on a set of services, currently locally hosted:

```
BASE_URL = http://localhost:8001
```

### Required Endpoints:

* `/research/search`
* `/research/read`
* `/research/summarise`
* `/jobs/`
* `/jobs/save`
* `/match/`
* `/email/`

---