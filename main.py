import re
from groq import Groq
from config import settings
from database import init_db, save_audit
from vector_store import query_style

# Init Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)

def audit_content(content_type: str, original_content: str):
    print("\n🤔 Agent lagi mikir... nyari gaya lu + nge-audit...")

    # 1. Ambil konteks gaya dari ChromaDB (RAG)
    styles = query_style(original_content)
    style_context = "\n".join(styles) if styles else "Belum ada gaya referensi."

    # 2. Bikin prompt buat LLM
    system_prompt = f"""Kamu adalah CreatorOps AI Agent, mentor konten yang jujur, tegas, dan santai.

GAYA KONTEN CREATOR INI (WAJIB IKUTI):
{style_context}

TUGAS:
Koreksi draf konten berikut. Kasih nilai 1-10 dan feedback yang to the point.

FORMAT OUTPUT WAJIB:
SCORE: [angka 1-10]
FEEDBACK: [kritik + saran perbaikan yang konkret]
"""

    # 3. Panggil Groq (pake model dari config.py lu)
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Tipe: {content_type}\nDraf: {original_content}"}
        ],
        temperature=0.7
    )

    full_text = response.choices[0].message.content

    # 4. Parsing SCORE pake Regex biar bisa masuk DB
    score_match = re.search(r"SCORE.*?(\d+)", full_text, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 0
    # Clamp score 0-10 biar aman
    score = max(0, min(10, score))

    # 5. Simpen ke SQLite
    save_audit(content_type, original_content, full_text, score)

    return score, full_text


if __name__ == "__main__":
    init_db()
    print("=== CreatorOps V1 - Script Auditor Agent ===")
    print(f"Model: {settings.MODEL_NAME}")
    print("Ketik 'exit' buat keluar.\n")

    while True:
        content_type = input("Tipe konten (script/caption) : ")
        if content_type.lower() == "exit":
            break

        original = input("Paste draf lu : ")
        if original.lower() == "exit":
            break

        try:
            score, feedback = audit_content(content_type, original)
            print("\n" + "="*50)
            print(f"⭐ SCORE: {score}/10")
            print(f"📝 FEEDBACK:\n{feedback}")
            print("="*50 + "\n")
        except Exception as e:
            print(f"❌ Error: {e}")