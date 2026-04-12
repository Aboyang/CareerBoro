from tools import browse_internet, read_webpage, full_research, match_job_resume, fetch_jobs
from model import model
from system_prompt import SYSTEM_PROMPT
from langchain.agents import create_agent
from langchain.messages import AIMessage, ToolMessage, HumanMessage
from langchain_core.callbacks import StdOutCallbackHandler

# --- Initialize agent ---
research_agent = create_agent(
    model=model,
    tools=[browse_internet, read_webpage, full_research, match_job_resume, fetch_jobs],
    system_prompt=SYSTEM_PROMPT
)

# RUN

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

content = f"""
Research for me software engineering internship in Singapore and find the best match for me.
Here is my resume: {SAMPLE_RESUME}
"""
            
result = research_agent.invoke(
    { "messages": [{ "role": "user", "content": content }] }
    , config={
        "callbacks": [StdOutCallbackHandler()],
    }
)

# Conversation
for message in result["messages"]:

    if type(message) == AIMessage:
        print("### AI MESSAGE ###")
        if message.tool_calls:
            print(message.tool_calls, "\n")
        if message.content:
            print(message.content, "n")

    if type(message) == ToolMessage:
        print("### TOOL MESSAGE ###")
        print(message.name)
        print(message.content, "\n")

    if type(message) == HumanMessage:
        print("### HUMAN MESSAGE ###")
        print(message.content, "\n")