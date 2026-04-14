from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import research, jobs, match, email

app = FastAPI()

app.include_router(research.router)
app.include_router(jobs.router)
app.include_router(match.router)
app.include_router(email.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)