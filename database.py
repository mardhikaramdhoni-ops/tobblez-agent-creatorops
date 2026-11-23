import sqlite3
from datetime import datetime
from config import settings

def get_connection():
    # Konek ke file db yang ada di settings
    return sqlite3.connect(settings.SQLITE_DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Task: Bikin table audits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT,
            original_content TEXT,
            ai_feedback TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("🗄️ SQLite Database & Table 'audits' Ready!")

def save_audit(content_type, original_content, ai_feedback, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audits (content_type, original_content, ai_feedback, score)
        VALUES (?, ?, ?, ?)
    ''', (content_type, original_content, ai_feedback, score))
    conn.commit()
    conn.close()
    print("✅ Audit saved to database!")

# Test run
if __name__ == "__main__":
    init_db()
    # Coba save data dummy buat ngetes
    save_audit("script", "Halo ini draf script video AI gue", "Bagus tapi kurang hook", 8)