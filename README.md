# CareerBoro

<img width="280" height="187" alt="Screenshot 2026-04-17 at 1 14 08 AM" src="https://github.com/user-attachments/assets/6dd08164-9d57-4245-a360-17c5158e4650" />
<img width="280" height="187" alt="Screenshot 2026-04-17 at 1 16 43 AM" src="https://github.com/user-attachments/assets/4e4459c4-6fd0-4eb5-b361-89a8bbcb736a" />

## Introduction

**CareerBoro** is a **Platform-as-an-Agent (PAaaS)** system designed to streamline the job search and application workflow.

The platform is decomposed into **four independent microservices**, each exposing a RESTful API, and orchestrated by a **LangChain-powered agent** that serves as the central intelligence layer.

Users interact with the system through two primary interfaces:

* **Conversational Chat UI**
  * Real-time streaming of agent reasoning
  * Tool-call trace visibility
    
* **Structured Dashboard**
  * Job listings
  * Match scores
  * Interview sessions

Additionally, a **settings panel** allows users to:

* Configure target roles, experience levels, and locations
* Upload resumes, which are parsed into structured candidate profiles

---

## Important Documentation

Please refer to the following for deeper understanding:

* [Folder Structure](./Documentation/Folder%20Structure.md)
* [Service Endpoints](./Documentation/Service%20Endpoints.md)
* [Agent Architecture](./Documentation/Agent%20Architecture%20Documentation.md)

---

## System Overview

* **`api/`** → Service layer

  * Encapsulates core logic and exposes it as RESTful APIs
  * Includes both internal services and external API integrations
  * Designed to be modular, reusable, and independently scalable

* **`backend/`** → Application backend

  * Orchestrates workflows between frontend and services
  * Hosts the LangChain agent (`backend/agent/`) - [Check out the agent here](./Documentation/Agent%20Architecture%20Documentation.md)

* **`frontend/`** → User interface

  * Chat interface + dashboard + settings panel

---

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux OR source venv\Scripts\activate # Window
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Keys

```bash
# AI Models
OPENAI_API_KEY=
REALTIME_API_KEY=

# Tools
SERPAPI_API_KEY=
RESEND_API_KEY=

# AWS Configuration
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=

# LangSmith (optional but recommended for tracing agent reasoning/workflow)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=
```
---

## Running the Services

### Start API Services

```bash
cd api
uvicorn main:app --reload --port=8001
```

### Start Backend

```bash
cd backend
uvicorn main:app --reload --port=8000
```

### Start Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Architecture Philosophy

CareerBoro follows a **loosely coupled, agent-centric architecture**:

* The **agent** acts as the decision-maker
* The **API layer** acts like external services (even internally)
* The **backend** orchestrates execution
* The **frontend** focuses purely on user experience

This separation allows:

* Independent scaling of services
* Clear abstraction boundaries
* Easier extension (new tools, services, or agents)

---

## Future Improvements

* Multi-agent specialization (research, outreach, job matching)
* Persistent memory and user profiling
* Advanced observability and tracing
* Deployment to cloud infrastructure

---
