from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse
from app.services.agent import stream_generate_ideas

router = APIRouter()

@router.get("/generate/stream")
async def generate_ideas_stream(topic: str = Query(..., description="Topik konten")):
    """
    [SSE Endpoint] Stream ide konten secara realtime dari Groq LLM.
    """
    try:
        async def event_publisher():
            async for chunk in stream_generate_ideas(topic):
                yield {
                    "event": "message",
                    "data": chunk
                }
            yield {
                "event": "end",
                "data": "[DONE]"
            }

        return EventSourceResponse(event_publisher())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming Error: {str(e)}")