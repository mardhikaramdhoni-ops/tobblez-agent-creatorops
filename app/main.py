# app/main.py
from pathlib import Path # <--- 1. TAMBAH IMPORT INI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.router import api_router
from app.db.database import init_db

# 1. Init Database SQLite
init_db()

# 2. Inisialisasi FastAPI App
app = FastAPI(
    title="CreatorOps AI Agent Microservice",
    description="Production-Ready API dengan SSE Realtime Streaming & RAG Orchestration.",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 3. Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include API V1 Router
app.include_router(api_router, prefix="/api/v1")

# 5. Health Check Endpoint
@app.get("/api/health", tags=["Health Check"])
async def health_check():
    return {
        "status": "online",
        "service": "CreatorOps API V4.0",
        "docs": "http://localhost:8000/docs"
    }

# 6. MOUNT FRONTEND SECARA DINAMIS
# Mengambil path folder 'frontend' yang ada di sebelah file main.py ini
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")