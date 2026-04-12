"""
job_desc_resume_match.py

Full hybrid JD ↔ Resume matching using:
  1. LLM extraction  — structured parsing of JD requirements & resume profile
  2. Keyword match   — hard skill set intersection
  3. Embedding sim   — semantic cosine similarity (text-embedding-3-small)
  4. LLM judge       — holistic scoring with reasoning (gpt-4o)
"""

from __future__ import annotations

import json
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from openai import OpenAI

load_dotenv()  # Load environment variables from .env file (for local development)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

@dataclass
class JDRequirements:
    role_title: str
    required_skills: list[str]
    nice_to_have_skills: list[str]
    min_years_experience: Optional[int]
    education_requirement: Optional[str]
    responsibilities: list[str]
    raw: dict = field(default_factory=dict)


@dataclass
class ResumeProfile:
    name: Optional[str]
    skills: list[str]
    total_years_experience: Optional[int]
    education: Optional[str]
    past_roles: list[str]
    highlights: list[str]
    raw: dict = field(default_factory=dict)


@dataclass
class MatchResult:
    overall_score: int                    # 0–100
    keyword_score: float                  # 0–100
    embedding_score: float                # 0–100
    llm_judge_score: int                  # 0–100
    matched_skills: list[str]
    missing_skills: list[str]
    bonus_skills: list[str]               # candidate has but JD didn't require
    strengths: list[str]
    gaps: list[str]
    recommendation: str                   # e.g. "Strong Match", "Partial Match", "Poor Match"
    summary: str


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class JobDescResumeMatch:
    """
    Hybrid JD ↔ Resume matcher.

    Usage:
        matcher = JobDescResumeMatch(job_desc=jd_text, resume_string=resume_text)
        result  = matcher.compute_match()
        print(result)
    """

    # Weights for the final blended score
    WEIGHT_KEYWORD   = 0.25
    WEIGHT_EMBEDDING = 0.25
    WEIGHT_LLM_JUDGE = 0.50

    def __init__(
        self,
        job_desc: str,
        resume_string: str,
    ):
        self.job_desc       = job_desc.strip()
        self.resume_string  = resume_string.strip()
        self.llm_model      = "gpt-4.1-mini"
        self.embedding_model = "text-embedding-3-small"

        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # Cached results (computed lazily)
        self._jd_requirements:  Optional[JDRequirements] = None
        self._resume_profile:   Optional[ResumeProfile]  = None
        self._jd_embedding:     Optional[np.ndarray]     = None
        self._resume_embedding: Optional[np.ndarray]     = None

    # ------------------------------------------------------------------
    # Step 1 — LLM structured extraction
    # ------------------------------------------------------------------

    def extract_jd_requirements(self) -> JDRequirements:
        """Parse the job description into structured requirements."""
        if self._jd_requirements:
            return self._jd_requirements

        system = (
            "You are an expert HR analyst. Extract structured information from "
            "the job description provided by the user. "
            "Respond ONLY with a valid JSON object — no markdown, no explanation."
        )
        schema = {
            "role_title": "string",
            "required_skills": ["list of strings"],
            "nice_to_have_skills": ["list of strings"],
            "min_years_experience": "integer or null",
            "education_requirement": "string or null",
            "responsibilities": ["list of strings — top 5 key responsibilities"],
        }
        user = (
            f"Job Description:\n{self.job_desc}\n\n"
            f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        raw = self._chat(system, user)
        data = self._parse_json(raw)

        self._jd_requirements = JDRequirements(
            role_title=data.get("role_title", ""),
            required_skills=self._normalise_list(data.get("required_skills", [])),
            nice_to_have_skills=self._normalise_list(data.get("nice_to_have_skills", [])),
            min_years_experience=data.get("min_years_experience"),
            education_requirement=data.get("education_requirement"),
            responsibilities=data.get("responsibilities", []),
            raw=data,
        )
        return self._jd_requirements

    def extract_resume_profile(self) -> ResumeProfile:
        """Parse the resume into a structured profile."""
        if self._resume_profile:
            return self._resume_profile

        system = (
            "You are an expert resume parser. Extract structured information from "
            "the resume provided by the user. "
            "Respond ONLY with a valid JSON object — no markdown, no explanation."
        )
        schema = {
            "name": "string or null",
            "skills": ["list of strings — all technical and soft skills mentioned"],
            "total_years_experience": "integer or null — estimate if not explicit",
            "education": "string or null — highest degree + field",
            "past_roles": ["list of strings — job titles held"],
            "highlights": ["list of strings — top 5 accomplishments or standout points"],
        }
        user = (
            f"Resume:\n{self.resume_string}\n\n"
            f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        raw = self._chat(system, user)
        data = self._parse_json(raw)

        self._resume_profile = ResumeProfile(
            name=data.get("name"),
            skills=self._normalise_list(data.get("skills", [])),
            total_years_experience=data.get("total_years_experience"),
            education=data.get("education"),
            past_roles=data.get("past_roles", []),
            highlights=data.get("highlights", []),
            raw=data,
        )
        return self._resume_profile

    # ------------------------------------------------------------------
    # Step 2 — Keyword / hard-skill match
    # ------------------------------------------------------------------

    def keyword_match_score(self) -> dict:
        """
        Fuzzy skill matching: a required skill phrase is considered matched if
        ANY candidate skill token appears within it, or vice versa.
        e.g. "fastapi or django rest framework" is matched by resume skill "fastapi".
        Returns score (0–100) plus matched / missing / bonus skill lists.
        """
        jd  = self.extract_jd_requirements()
        res = self.extract_resume_profile()

        required_phrases  = [s.lower() for s in jd.required_skills]
        nice_phrases      = [s.lower() for s in jd.nice_to_have_skills]
        candidate_skills  = [s.lower() for s in res.skills]

        def fuzzy_match(phrase: str, candidates: list[str]) -> str | None:
            """Return the first candidate skill that partially matches the phrase."""
            for skill in candidates:
                if skill in phrase or phrase in skill:
                    return skill
            return None

        matched  = []   # (required_phrase, matched_candidate_skill)
        missing  = []   # required phrases with no match

        for phrase in required_phrases:
            hit = fuzzy_match(phrase, candidate_skills)
            if hit:
                matched.append((phrase, hit))
            else:
                missing.append(phrase)

        nice_matched = []
        for phrase in nice_phrases:
            if fuzzy_match(phrase, candidate_skills):
                nice_matched.append(phrase)

        # Bonus: candidate skills not covered by any required or nice-to-have phrase
        all_jd_phrases = required_phrases + nice_phrases
        bonus = [
            skill for skill in candidate_skills
            if not any(skill in p or p in skill for p in all_jd_phrases)
        ]

        base_score = (len(matched) / len(required_phrases) * 100) if required_phrases else 100.0
        boost      = (len(nice_matched) / len(nice_phrases) * 10) if nice_phrases else 0.0
        score      = min(100.0, base_score + boost)

        return {
            "score": round(score, 1),
            "matched_skills":       sorted(set(m[1] for m in matched)),
            "missing_skills":       sorted(missing),
            "bonus_skills":         sorted(set(bonus)),
            "nice_to_have_matched": sorted(nice_matched),
        }

    # ------------------------------------------------------------------
    # Step 3 — Embedding cosine similarity
    # ------------------------------------------------------------------

    def embedding_similarity_score(self) -> float:
        """
        Embed the full JD and resume texts, compute cosine similarity.
        Returns a score 0–100.
        """
        jd_vec  = self._get_embedding(self.job_desc)
        res_vec = self._get_embedding(self.resume_string)
        cosine  = self._cosine_similarity(jd_vec, res_vec)
        # text-embedding-3-small cosine for related docs sits ~0.5–1.0
        # Rescale [0.5, 1.0] → [0, 100] so 0.75 cosine → 50, 1.0 → 100
        LOW, HIGH = 0.5, 1.0
        score = max(0.0, min(100.0, (cosine - LOW) / (HIGH - LOW) * 100))
        return round(score, 1)

    # ------------------------------------------------------------------
    # Step 4 — LLM holistic judge
    # ------------------------------------------------------------------

    def llm_judge_score(self) -> dict:
        """
        Ask the LLM to holistically score the match with structured reasoning.
        """
        jd  = self.extract_jd_requirements()
        res = self.extract_resume_profile()

        system = (
            "You are a senior technical recruiter with 15 years of experience. "
            "Given a structured job description and candidate profile, provide a "
            "holistic match assessment. "
            "Respond ONLY with a valid JSON object — no markdown, no explanation."
        )
        schema = {
            "score": "integer 0–100",
            "strengths": ["list of strings — top 3–5 reasons the candidate fits"],
            "gaps": ["list of strings — top 3–5 concerns or missing areas"],
            "recommendation": "one of: Strong Match | Good Match | Partial Match | Poor Match",
            "summary": "string — 2–3 sentence recruiter summary",
        }
        user = (
            f"Job Requirements:\n{json.dumps(jd.raw, indent=2)}\n\n"
            f"Candidate Profile:\n{json.dumps(res.raw, indent=2)}\n\n"
            f"Return JSON matching this schema:\n{json.dumps(schema, indent=2)}"
        )

        raw  = self._chat(system, user)
        data = self._parse_json(raw)
        return data

    # ------------------------------------------------------------------
    # Orchestrator — compute_match()
    # ------------------------------------------------------------------

    def compute_match(self) -> MatchResult:
        """
        Run all steps and return a unified MatchResult.

        Pipeline:
          1. Extract JD requirements  (LLM)
          2. Extract resume profile   (LLM)
          3. Keyword match score
          4. Embedding similarity
          5. LLM judge score
          6. Weighted blend → overall score
        """
        print("[1/5] Extracting JD requirements...")
        self.extract_jd_requirements()

        print("[2/5] Extracting resume profile...")
        self.extract_resume_profile()

        print("[3/5] Computing keyword match...")
        kw = self.keyword_match_score()

        print("[4/5] Computing embedding similarity...")
        emb_score = self.embedding_similarity_score()

        print("[5/5] Running LLM judge...")
        judge = self.llm_judge_score()

        # --- Weighted blend ---
        keyword_score   = kw["score"]
        llm_judge_score = judge.get("score", 50)

        overall = (
            keyword_score   * self.WEIGHT_KEYWORD   +
            emb_score       * self.WEIGHT_EMBEDDING +
            llm_judge_score * self.WEIGHT_LLM_JUDGE
        )

        return MatchResult(
            overall_score=round(overall),
            keyword_score=keyword_score,
            embedding_score=emb_score,
            llm_judge_score=llm_judge_score,
            matched_skills=kw["matched_skills"],
            missing_skills=kw["missing_skills"],
            bonus_skills=kw["bonus_skills"],
            strengths=judge.get("strengths", []),
            gaps=judge.get("gaps", []),
            recommendation=judge.get("recommendation", ""),
            summary=judge.get("summary", ""),
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _chat(self, system: str, user: str) -> str:
        response = self.client.chat.completions.create(
            model=self.llm_model,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return response.choices[0].message.content.strip()

    def _get_embedding(self, text: str) -> np.ndarray:
        """Return a unit-normalised embedding vector."""
        # Cache by identity (jd vs resume)
        if text is self.job_desc and self._jd_embedding is not None:
            return self._jd_embedding
        if text is self.resume_string and self._resume_embedding is not None:
            return self._resume_embedding

        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        vec /= np.linalg.norm(vec) + 1e-10   # L2 normalise

        if text is self.job_desc:
            self._jd_embedding = vec
        else:
            self._resume_embedding = vec
        return vec

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b))  # both are already unit-normalised

    @staticmethod
    def _normalise_list(items: list) -> list[str]:
        """Lowercase-strip each item, remove empty strings."""
        return [str(i).strip() for i in items if str(i).strip()]

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Strip markdown fences and parse JSON safely."""
        clean = text.strip()
        if clean.startswith("```"):
            lines = clean.splitlines()
            clean = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(clean)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON:\n{clean}\n\nError: {e}") from e


# ---------------------------------------------------------------------------
# Example usage / smoke test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    SAMPLE_JD = """
About Team

AI is reshaping the technology landscape, but strong engineering fundamentals remain critical. The AI Ignite Internship Programme (AIIP) is designed to create meaningful pathways for engineering students to gain hands-on, real-world experience building AI-powered products. This programme bridges the gap between academic learning and industry application by immersing interns in practical AI engineering work, beyond theoretical exercises.
Job Description

Participate in the AI Ignite Internship Programme, working in a startup-like, fast-paced environment to explore and experiment with AI-driven solutions
Experiment with AI-powered ideas, prototypes, tools, and workflows, moving quickly from concept to iteration
Apply and refine AI concepts such as prompting, automation, system integration, and model evaluation through hands-on work
Collaborate closely with mentors across engineering, product, and AI research, taking ownership of exploratory initiatives
Contribute to internal experiments and projects where problem statements may be loosely defined, requiring initiative and independent thinking
Share insights, experiments, and learnings with peers and stakeholders throughout and at the end of the programme
Requirements

Preferably pursuing a degree in Computer Science, Computer Engineering, Electrical Engineering, Information Systems, Mathematics, or a related engineering field
Deep passion for AI and emerging technologies, demonstrated through self-driven exploration, personal projects, tools used, or workflows built
Actively keeps up with the AI landscape (e.g. new models, tools, platforms, research trends, or real-world applications)
Has integrated AI into daily work or learning (e.g. coding, studying, research, automation, productivity, experimentation)
Comfortable operating in a startup environment with ambiguity, fast iteration cycles, and minimal hand-holding
Strong problem-solving mindset with a willingness to experiment, fail fast, and iterate
Self-motivated, curious, and eager to build, tinker, and push boundaries in a rapidly evolving space
Preferably able to start in March 2026 and commit to the programme for a minimum duration of 6 months (part time/full time) or 3 months (full time) 
    """

    SAMPLE_RESUME = """
Tee Kai Yang
Singapore
+65 9193 8090
tkaiyang2005@gmail.com
www.linkedin.com/in/kaiyangtee | https://github.com/Aboyang
EDUCATION
Nanyang Technological University, Singapore Bachelor of Applied Computing in Finance
§ Current CGPA: 4.53/5 (First Class Honors)
§ Awards: Dean’s List AY2024/2025, Hee Chong Meo Scholarship
WORK EXPERIENCES
Aug 2024 – May 2028 (Expected)
Full-Stack AI Engineer Intern, Pencil Labs Nov 2025 – Jan 2026
§ Co-developed QueryLabs, a B2B SaaS hybrid RAG (Retrieval-augmented generation) platform with Qdrant, enabling explainable
enterprise document querying across large multi-file knowledge bases.
§ Delivered enterprise-facing features relating to AI chat interface, interactive document viewer, knowledge base management
system in 2 weeks, built with Next.js, TypeScript, TailwindCSS, and Supabase.
§ Involved in citation provenance pipeline, designing the citation schema and rendering bounding box and source metadata for
retrieved document chunks to improve trustworthiness and auditability.
Software Engineer, NTU Investment Interactive Club Sep 2024 – Aug 2025
§ Revamped the club’s website with UX/UI improvements, driving a 176% increase in users and a 15.3% boost in engagement rate.
§ Engineered an automation pipeline using Zapier and prompt engineering to distribute of financial newsletters to 50+ members.
FEATURED PROJECTS
ParkPulse | AWS, React, Node.js, OneMap API, Redis, Nginx March 2026 to Present
§ Developed an application to locate nearest carparks to a destination, view real-time slot availability, and navigate to them.
§ Integrated OneMap API for geocoding and nearby carparks search, and data.gov.sg API for live availability data.
§ Implemented AWS Cognito and DynamoDB for secure user authentication and preference management.
§ Optimized high-read carpark data requests with Redis caching, reducing API latency by 18×.
§ Optimized system throughput by 20% through a load balancer across 5 server instances during peak trajic simulation.
Interview Pal | LangChain, OpenAI Realtime API, Supabase, FastAPI, React, Redux Jan 2026
§ Built an interview preparation platform with a real-time convo AI in voice mode.
§ Orchestrated a LangChain architecture, giving the agent tool access to Supabase storage, PDF parsing utility, and NLP extraction.
§ Prompt-engineered GPT-3.5-turbo model to produce reliable, structured JSON outputs throughout the pipeline.
§ Optimized real-time voice conversation using OpenAI Realtime SDK, maintaining stateful conversations with low-latency
responses (avg. 648 ms).
Stock Wizard | React.js, Redux, Node.js, Chart.js, Yahoo Finance API, Firebase Aug 2025
§ Developed a full-stack stock analytics platform, enabling beginner investors to screen stocks in real-time, perform quantitative
analysis with interactive visualizations and educational tooltips.
§ Integrated Firebase Auth and Firestore for real-time synchronization and secure user authentication.
HACKATHONS & COMPETITIONS
§ Batch 09 International Hackathon 2025 – 1st Place
§ NTU FinTech Essay Challenge 2025 – 2nd Place
§ NTU IEEE x Jane Street Coding Challenge 2025 – 3rd Place
LEADERSHIP EXPERIENCE
§ Baringa Inter-Varsity Trading Competition 2025 – Finalist
§ Beyond Binary Hackathon 2026
§ HacknRoll 2026
Founding President, Nanyang FinTech Catalyst Oct 2024 – Present
§ Spearheaded growth strategy that expanded members headcount from 5 to 140+ within a year.
§ Leading a team of 10 executive committees, launching Quant Finance Academy and FinTech Exploration Hub.
§ Pioneered FinSight Series, a four-part event featuring industry professionals from SFA, PwC, and Sea, engaging 150+ participants.
§ Delivered 6 talks averaging 30–60 attendees per session, covering topics including AI, blockchain, and FinTech.
SKILLS & TOOLS
Programming Languages: JavaScript (TypeScript, Node.js), Python (Pandas, PyTorch, Scikit-Learn), Java, R
Tools: Next.js, React.js, Redux, FastAPI, Supabase, Firebase, AWS, Qdrant, LangChain, LangGraph, LangSmith, Ollama, Redis, Claude
Concepts: Object-Oriented Programming, Data Structures & Algorithms, Structured Query Language (SQL), REST APIs, System Design,
Cloud Computing, Neural Network, Natural Language Processing, Prompt Engineering, Retrieval Augmented Generation, Agentic AI
"""

    matcher = JobDescResumeMatch(job_desc=SAMPLE_JD, resume_string=SAMPLE_RESUME)
    result  = matcher.compute_match()

    print("\n" + "="*60)
    print(f"  MATCH RESULT: {result.recommendation}")
    print("="*60)
    print(f"  Overall Score   : {result.overall_score}/100")
    print(f"  Keyword Score   : {result.keyword_score}/100  (weight 25%)")
    print(f"  Embedding Score : {result.embedding_score}/100  (weight 25%)")
    print(f"  LLM Judge Score : {result.llm_judge_score}/100  (weight 50%)")
    print()
    print(f"  Matched Skills  : {', '.join(result.matched_skills) or 'none'}")
    print(f"  Missing Skills  : {', '.join(result.missing_skills) or 'none'}")
    print(f"  Bonus Skills    : {', '.join(result.bonus_skills) or 'none'}")
    print()
    print("  Strengths:")
    for s in result.strengths:
        print(f"    ✓ {s}")
    print("  Gaps:")
    for g in result.gaps:
        print(f"    ✗ {g}")
    print()
    print(f"  Summary: {result.summary}")
    print("="*60)