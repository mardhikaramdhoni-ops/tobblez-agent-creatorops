from fastapi import APIRouter
from app.api.v1.endpoints import ideas, audit, styles

api_router = APIRouter()

# 1. Endpoint Generate Ide (SSE Streaming)
api_router.include_router(ideas.router, prefix="/ideas", tags=["Ideas Engine"])

# 2. Endpoint Audit Naskah
api_router.include_router(audit.router, prefix="/audit", tags=["Script Doctor & Audit"])

# 3. Endpoint Vector DB Style Engine
api_router.include_router(styles.router, prefix="/styles", tags=["Style Engine (ChromaDB RAG)"])