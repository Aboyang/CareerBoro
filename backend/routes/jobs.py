# from fastapi import APIRouter
# from services.job_db import JobDB
# from typing import List, Dict, Any

# router = APIRouter(prefix="/jobs", tags=["jobs"])

# job_db = JobDB()

# @router.get("/", response_model=List[Dict[str, Any]])
# def get_jobs():
#     return job_db.get_jobs()

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.job_db import JobDB
from services.job_broadcaster import broadcaster
from typing import List, Dict, Any
import asyncio

router = APIRouter(prefix="/jobs", tags=["jobs"])

job_db = JobDB()


@router.get("/", response_model=List[Dict[str, Any]])
def get_jobs():
    return job_db.get_jobs()


@router.websocket("/ws")
async def websocket_jobs(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        # Send current jobs immediately on connect
        jobs = job_db.get_jobs()
        await websocket.send_json(jobs)

        # Keep connection alive with a heartbeat
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Connection error: {e}")
        broadcaster.disconnect(websocket)