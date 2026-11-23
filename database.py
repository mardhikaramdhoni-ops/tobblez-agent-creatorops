"""
database.py - SQLite Database Layer for CreatorOps AI Agent
Handles both Audit History (V1) and Generated Content Ideas (V2).
"""
import sqlite3
import logging
from typing import List, Dict, Any

# Setup Logger
logger = logging.getLogger("CreatorOps.Database")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

DB_NAME = "creatorops.db"


def get_connection():
    """Mengembalikan koneksi SQLite dengan Row Factory agar hasil query berupa Dict."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Membuat tabel 'audits' dan 'ideas' jika belum ada."""
    logger.info("🛠️ Initializing SQLite Database tables...")
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tabel V1.0: Audit History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_script TEXT NOT NULL,
                feedback TEXT NOT NULL,
                revised_script TEXT NOT NULL,
                score INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabel V2.0: Viral Content Ideas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                hook TEXT NOT NULL,
                concept TEXT NOT NULL,
                source_links TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
    logger.info("✅ Database tables initialized successfully.")


# --- FUNCTION V1.0 (AUDITS) ---
def save_audit(original: str, feedback: str, revised: str, score: int) -> int:
    """Nyimpen hasil audit script ke database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audits (original_script, feedback, revised_script, score)
            VALUES (?, ?, ?, ?)
            """,
            (original, feedback, revised, score)
        )
        conn.commit()
        logger.info(f"💾 Saved audit log to DB (ID: {cursor.lastrowid})")
        return cursor.lastrowid


# --- FUNCTION V2.0 (IDEAS) ---
def save_idea(topic: str, hook: str, concept: str, source_links: str = "") -> int:
    """
    Nyimpen ide konten hasil riset tren ke database.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ideas (topic, hook, concept, source_links)
            VALUES (?, ?, ?, ?)
            """,
            (topic, hook, concept, source_links)
        )
        conn.commit()
        logger.info(f"💡 Saved Content Idea to DB (ID: {cursor.lastrowid})")
        return cursor.lastrowid


def get_recent_ideas(limit: int = 5) -> List[Dict[str, Any]]:
    """Mengambil riwayat ide konten terbaru."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, topic, hook, concept, source_links, created_at FROM ideas ORDER BY id DESC LIMIT ?", 
            (limit,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# --- TEST RUNNER (ISOLATED TEST) ---
if __name__ == "__main__":
    print("🧪 Testing Database V2 Schema...")
    init_db()
    
    # Dummy Test Insert Idea
    test_id = save_idea(
        topic="AI Puncak Bogor",
        hook="Polisi Bogor Pake AI Buat Macet? Gini Cara Kerjanya!",
        concept="Bahas inovasi AI lokal di Jalur Puncak, angle: Efisiensi vs Privasi.",
        source_links="https://news.google.com/..."
    )
    
    recent = get_recent_ideas(limit=1)
    print("\n--- RETRIEVED IDEA FROM DB ---")
    print(recent)