from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.db.database import init_db

# 1. Init Database SQLite pas server nyala
init_db()

# 2. Inisialisasi FastAPI App
app = FastAPI(
    title="CreatorOps AI Agent Microservice",
    description="Production-Ready API dengan SSE Realtime Streaming & RAG Orchestration.",
    version="3.0.0",
    docs_url="/docs",      # Auto Swagger UI
    redoc_url="/redoc"
)

# 3. Setup CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Nanti pas prod ganti domain frontend lu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include API V1 Router
app.include_router(api_router, prefix="/api/v1")

# 5. Root Health Check Endpoint
@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "service": "CreatorOps API V3.0",
        "docs": "http://localhost:8000/docs"
    }