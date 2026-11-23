"""
main.py - CreatorOps AI Agent Interactive CLI (V2.0 Complete)
Co-Pilot untuk Content Creator: Script Audit, Trend Research, & Viral Ideation.
"""
import sys
import logging
import database as db
import vector_store as vs
from agent import generate_viral_ideas

# Setup Logger (Quiet down info logs for cleaner CLI user experience)
logging.basicConfig(level=logging.ERROR)


def print_banner():
    print("""
====================================================================
 🕶️🩹 CREATOROPS AI AGENT v2.0 - Autonomous Creator Co-Pilot
 Powered by Groq (gpt-oss-120b), ChromaDB RAG, Google News, & SQLite
====================================================================
""")


def menu_audit_script():
    """Flow Audit Script (Fitur V1.0)"""
    print("\n--- 📝 AUDIT & POLES SCRIPT KONTEN (V1.0) ---")
    script_input = input("Masukkan draft script/caption lu: ").strip()
    
    if not script_input:
        print("❌ Script tidak boleh kosong!")
        return

    print("\n🔍 Analisis gaya penulisan & auditing sedang berjalan...")
    # Import main audit log logic jika diperlukan atau panggil dari modul audit
    # Untuk simplifikasi CLI V2.0, kita panggil pipeline riset atau audit
    style = vs.search_similar_styles(script_input)
    
    # Fast mockup call ke LLM untuk audit (Menggunakan agent/groq)
    from groq import Groq
    from config import settings
    import re
    
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    prompt = f"""
Lu adalah Senior Content Editor. Audit script berikut berdasarkan gaya penulisan ini:
--- GAYA PENULISAN ---
{style}

--- SCRIPT ORIGINAL ---
{script_input}

Berikan output persis format ini:
--- FEEDBACK ---
(Poin perbaikan)

--- REVISED SCRIPT ---
(Hasil revisi script)

SCORE: (Angka 1-100)
"""
    res = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    
    output = res.choices[0].message.content
    print("\n" + output)
    
    # Extract Score & Save to DB
    score_match = re.search(r"SCORE:\s*(\d+)", output)
    score = int(score_match.group(1)) if score_match else 80
    
    db.save_audit(original=script_input, feedback=output, revised=output, score=score)
    print("\n✅ Hasil audit berhasil disimpan ke Database SQLite!")


def menu_research_trends():
    """Flow Riset Tren & Ideation (Fitur V2.0)"""
    print("\n--- 🚀 RISET TREN & IDE KONTEN VIRAL (V2.0) ---")
    topic = input("Masukkan topik/niche yang mau diriset (misal: 'AI', 'Macet Bogor', 'Tips Coding'): ").strip()
    
    if not topic:
        print("❌ Topik tidak boleh kosong!")
        return

    try:
        num_ideas = int(input("Berapa ide yang mau di-generate? (Default: 3): ") or "3")
    except ValueError:
        num_ideas = 3

    print(f"\n🔍 Agent sedang menerobos internet untuk mencari tren '{topic}'...")
    results = generate_viral_ideas(topic=topic, num_ideas=num_ideas)

    if not results:
        print("❌ Gagal membuat ide. Coba topik lain.")
        return

    print(f"\n✨ SUCCESS! Dihasilkan {len(results)} Ide Konten Viral (Auto-saved to DB):\n")
    for idx, idea in enumerate(results, start=1):
        print(f"💡 IDE #{idx} [DB ID: {idea['id']}]")
        print(f"🔥 HOOK        : {idea['hook']}")
        print(f"📌 KONSEP      : {idea['concept']}")
        print(f"🔗 REFERENSI   : {idea['source_links']}")
        print("-" * 65)


def menu_add_style():
    """Flow Tambah Persona Gaya ke ChromaDB"""
    print("\n--- 🧠 TAMBAH GAYA PENULISAN (CHROMADB RAG) ---")
    sample_text = input("Masukkan contoh tulisan/caption khas lu:\n> ").strip()
    style_name = input("Nama label gaya (misal: 'santai_tech', 'edukatif_kasual'): ").strip() or "default"
    
    if sample_text:
        vs.add_style_sample(text=sample_text, style_name=style_name)
        print("✅ Gaya penulisan berhasil disimpan ke ChromaDB Vector Store!")
    else:
        print("❌ Teks sampel tidak boleh kosong!")


def menu_view_history():
    """Flow Lihat Riwayat SQLite DB"""
    print("\n--- 📜 RIWAYAT DATABASE SQLITE ---")
    print("1. Riwayat Ide Konten Viral (V2.0)")
    print("2. Riwayat Audit Script (V1.0)")
    choice = input("Pilih (1/2): ").strip()

    if choice == "1":
        ideas = db.get_recent_ideas(limit=5)
        if not ideas:
            print("Belum ada riwayat ide.")
            return
        print("\n--- 5 IDE TERAKHIR ---")
        for item in ideas:
            print(f"[{item['created_at']}] Topik: {item['topic']}")
            print(f"🔥 Hook: {item['hook']}\n")
    else:
        print("Menampilkan riwayat audit...")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, original_script, score, created_at FROM audits ORDER BY id DESC LIMIT 5")
            audits = cursor.fetchall()
            for a in audits:
                print(f"[{a['created_at']}] Score: {a['score']} | Script: {a['original_script'][:40]}...")


def main():
    db.init_db()
    print_banner()

    while True:
        print("\n📌 PILIH MENU:")
        print("1. 🚀 Riset Tren Web & Buat Ide Viral (V2.0)")
        print("2. 📝 Audit & Poles Script (V1.0)")
        print("3. 🧠 Tambah Contoh Gaya Penulisan (ChromaDB)")
        print("4. 📜 Lihat Riwayat Database")
        print("5. ❌ Keluar")
        
        choice = input("\nMasukkan pilihan (1-5): ").strip()

        if choice == "1":
            menu_research_trends()
        elif choice == "2":
            menu_audit_script()
        elif choice == "3":
            menu_add_style()
        elif choice == "4":
            menu_view_history()
        elif choice == "5":
            print("\n👋 Makasih bro Mumi Coder! Sampai jumpa di proyek MLOps berikutnya! 🕶️🩹")
            sys.exit(0)
        else:
            print("⚠️ Pilihan gak valid, coba lagi bro.")


if __name__ == "__main__":
    main()