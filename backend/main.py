from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import chat, jobs, resume
from services.job_db import JobDB
from services.job_broadcaster import broadcaster
import asyncio

job_db = JobDB()


async def watch_dynamodb_streams():
    while True:
        await asyncio.sleep(5)
        try:
            if job_db.has_new_stream_records():
                print("[Watcher] Change detected — broadcasting...")
                updated_jobs = job_db.get_jobs()
                print(f"[Watcher] Broadcasting {len(updated_jobs)} jobs to {len(broadcaster.connections)} clients")
                await broadcaster.broadcast(updated_jobs)
        except Exception as e:
            print(f"[Watcher] Error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the DynamoDB stream watcher on app startup
    asyncio.create_task(watch_dynamodb_streams())
    yield
    # Any shutdown cleanup can go here


app = FastAPI(lifespan=lifespan)

app.include_router(chat.router)
app.include_router(jobs.router)
app.include_router(resume.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)