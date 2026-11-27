import sqlite3
from app.core.config import settings

def init_db():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS idea_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            script_text TEXT,
            audit_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_audit_result(platform: str, script_text: str, audit_result: str) -> bool:
    """Menyimpan hasil audit naskah ke database SQLite."""
    try:
        conn = sqlite3.connect(settings.SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                script_text TEXT,
                audit_result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO audits (platform, script_text, audit_result) VALUES (?, ?, ?)",
            (platform, script_text, audit_result)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"\n[DB ERROR] Gagal simpan audit: {e}\n")
        return False