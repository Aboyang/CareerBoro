import os
from dotenv import load_dotenv
import json
import httpx
from fastapi import Request, Response, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from schema.interview import QuestionRequest
from services.question import InterviewQuestionPreparer

load_dotenv()
REALTIME_API_KEY = os.getenv("REALTIME_API_KEY")

router = APIRouter(
    prefix="/interview",
    tags=["interview"]
)

SESSION_CONFIG = {
    "session": {
        "type": "realtime",
        "model": "gpt-realtime",
        "audio": {
            "output": {
                "voice": "alloy"
            }
        }
    }
}

@router.post("/session")
async def create_session(request: Request):
    """
    Receives SDP from browser, forwards to OpenAI Realtime,
    returns SDP answer.
    """
    sdp = await request.body()
    print(sdp.decode())

    form_data = {
        "session": json.dumps(SESSION_CONFIG)
    }

    files = {
        "sdp": sdp
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://api.openai.com/v1/realtime/calls",
            headers={
                "Authorization": f"Bearer {REALTIME_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            },
            data=form_data,
            files=files
        )

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail=r.text)

    answer_sdp = r.text
    print(answer_sdp)

    return Response(content=answer_sdp, media_type="application/sdp")

@router.get("/token")
async def get_token():
    """
    Generates ephemeral token for browser WebRTC usage
    """
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.openai.com/v1/realtime/client_secrets",
                headers={
                    "Authorization": f"Bearer {REALTIME_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=SESSION_CONFIG
            )

        r.raise_for_status()
        return JSONResponse(content=r.json())

    except Exception as e:
        print("Token generation error:", e)
        raise HTTPException(status_code=500, detail="Failed to generate token")


@router.post("/questions")
async def get_questions(req: QuestionRequest):
    questions = InterviewQuestionPreparer().prepare_questions(req.role, req.company, req.job_desc, req.resume_context)
    return {"questions": questions}
