# app/api/v1/endpoints/ideas.py
import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from app.services.agent import stream_generate_ideas

router = APIRouter()

@router.get("/generate/stream")
async def generate_ideas_stream(
    topic: str, 
    platform: str = "Instagram Reels", 
    target_audience: str = "General"
):
    async def event_publisher():
        async for chunk in stream_generate_ideas(topic):
            # Bungkus dalam JSON agar karakter \n dan formatting tidak hilang di jalan
            payload = json.dumps({"text": chunk})
            yield {"data": payload}

    return EventSourceResponse(event_publisher())