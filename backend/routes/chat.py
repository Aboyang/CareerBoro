from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from services.stream import Streamer
from schema.chat import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])

streamer = Streamer()

@router.post("/stream")
async def streaming_response(request: ChatRequest):

    prompt = request.prompt

    # Stream the final response
    async def event_generator():
        async for chunk in streamer.stream(prompt):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/plain")