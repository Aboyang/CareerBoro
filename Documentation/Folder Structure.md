# Project Structure Overview

* **`api/`**
  Acts as a dedicated **service layer**, similar to external APIs on the internet. It encapsulates core business logic and exposes it through well-defined endpoints, including both internally implemented services and wrappers around external APIs. This separation ensures the logic remains decoupled from the main application and can be independently scaled or reused.

* **`backend/`**
  Represents the core application backend, responsible for orchestrating workflows, handling client requests, and interacting with the service layer. The `backend/agent/` module defines the LangChain-based agent, including its model, tools, and system behavior.

* **`frontend/`**
  Provides the user-facing interface, enabling interaction with the backend and agent through features such as chat, job tracking, and dashboards.

```plaintext
CareerAgent/
├── .env
├── .git
├── .gitignore
│
├── Documentation/
│   ├── Agent Architecture Documentation.md
│   └── Service Endpoints.md
│
├── api/
│   ├── main.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── email.py
│   │   ├── jobs.py
│   │   ├── match.py
│   │   └── research.py
│   ├── schemas/
│   │   ├── email.py
│   │   ├── job.py
│   │   ├── match.py
│   │   └── research.py
│   ├── services/
│   │   ├── job_db.py
│   │   ├── job_desc_resume_matcher.py
│   │   ├── job_scraper.py
│   │   ├── research.py
│   │   └── send_email.py
│   └── venv/
│
├── backend/
│   ├── main.py
│   ├── agent/
│   │   ├── agent.py
│   │   ├── model.py
│   │   ├── system_prompt.py
│   │   └── tools.py
│   ├── routes/
│   │   ├── chat.py
│   │   ├── interview.py
│   │   ├── jobs.py
│   │   └── resume.py
│   ├── schema/
│   │   ├── chat.py
│   │   └── interview.py
│   ├── services/
│   │   ├── job_broadcaster.py
│   │   ├── job_db.py
│   │   ├── question.py
│   │   ├── resume.py
│   │   └── stream.py
│   └── utils/
│       ├── db.py
│       └── pdf_to_string.py
│
├── frontend/
│   ├── .gitignore
│   ├── README.md
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── node_modules/
│   ├── public/
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── assets/
│       └── pages/
│           ├── chat/
│           │   ├── Chat.css
│           │   ├── Chat.jsx
│           │   ├── ChatInput.jsx
│           │   ├── ChatMessage.jsx
│           │   └── useStreamingMarkdown.jsx
│           ├── convoai/
│           │   ├── Button.jsx
│           │   ├── ConvoAI.css
│           │   ├── ConvoAI.jsx
│           │   ├── SessionControls.css
│           │   ├── SessionControls.jsx
│           │   ├── VoiceIndicator.css
│           │   └── VoiceIndicator.jsx
│           ├── dashboard/
│           │   ├── Dashboard.css
│           │   └── Dashboard.jsx
│           ├── jobboard/
│           │   ├── JobBoard.css
│           │   ├── JobBoard.jsx
│           │   ├── JobCard.jsx
│           │   └── JobDetail.jsx
│           └── settings/
│               ├── SettingsPanel.css
│               └── SettingsPanel.jsx
```