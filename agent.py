"""
agent.py - Core AI Orchestrator for CreatorOps
Handles Trend Researching, RAG Persona Injection, Content Generation, & DB Persistence.
"""
import logging
import json
from typing import List, Dict, Any
from groq import Groq

from config import settings
import database as db
import vector_store as vs
import tools

# Setup Logger
logger = logging.getLogger("CreatorOps.Agent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)


def generate_viral_ideas(topic: str, num_ideas: int = 3) -> List[Dict[str, Any]]:
    """
    Autonomous Pipeline:
    1. Riset Tren via Google News (tools.py)
    2. Retrieve Persona Gaya Penulisan via ChromaDB (vector_store.py)
    3. Synthesize dengan Groq LLM (gpt-oss-120b)
    4. Auto-save ke Database SQLite (database.py)
    """
    logger.info(f"🚀 [Agent Pipeline] Starting Trend & Ideation Pipeline for topic: '{topic}'")

    # STEP 1: Web Riset Tren
    logger.info("🔍 [Step 1/4] Web Researching trends...")
    search_results = tools.search_web(query=topic, max_results=5, lang="id")
    formatted_trends = tools.format_search_results_for_llm(search_results)

    # STEP 2: Retrieve Writing Style (RAG)
    logger.info("📚 [Step 2/4] Retrieving writing style from ChromaDB...")
    style_context = vs.search_similar_styles(query=topic, n_results=2)

    # STEP 3: Prompt Engineering & LLM Synthesis
    logger.info("🧠 [Step 3/4] Synthesizing Viral Ideas via Groq LLM...")
    
    system_prompt = f"""
Lu adalah AI Content Strategist & Viral Marketer tingkat dunia.
Tugas lu adalah menganalisis berita/tren terkini dan mengubahnya menjadi {num_ideas} ide konten media sosial (TikTok/Reels/X) yang SANGAT VIRAL.

--- GAYA PENULISAN & PERSONA NICHE (DARI CHROMADB) ---
{style_context}

--- TREN WEB REAL-TIME TERKINI ---
{formatted_trends}

--- ATURAN OUTPUT (STRICT JSON ONLY) ---
Lu HARUS mengembalikan output HANYA dalam format JSON Array (List of Objects) tanpa ada teks pembuka/penutup atau tag markdown ```json.
Setiap object dalam JSON harus memiliki struktur:
[
  {{
    "hook": "Judul/Kalimat 3 detik pertama yang bikin orang berhenti scrolling (Stop-scrolling Hook)",
    "concept": "Penjelasan rinci sudut pandang (angle) konten, struktur cerita, dan alasan kenapa ini bakal viral",
    "source_links": "Link berita referensi utama dari riset tren"
  }}
]
"""

    user_prompt = f"Tolong buatkan {num_ideas} ide konten viral terkini berdasarkan topik: '{topic}'."

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        raw_content = response.choices[0].message.content.strip()
        
        # Cleaning sanitize jika LLM ngeyel ngasih markdown block ```json
        if raw_content.startswith("```json"):
            raw_content = raw_content.replace("```json", "", 1)
        if raw_content.startswith("```"):
            raw_content = raw_content.replace("```", "", 1)
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
            
        ideas_data = json.loads(raw_content.strip())

        # STEP 4: Auto Persist to SQLite Database
        logger.info("💾 [Step 4/4] Saving generated ideas to SQLite Database...")
        saved_ideas = []
        for item in ideas_data:
            idea_id = db.save_idea(
                topic=topic,
                hook=item.get("hook", ""),
                concept=item.get("concept", ""),
                source_links=item.get("source_links", "")
            )
            saved_ideas.append({
                "id": idea_id,
                "topic": topic,
                "hook": item.get("hook", ""),
                "concept": item.get("concept", ""),
                "source_links": item.get("source_links", "")
            })

        logger.info(f"✅ [Agent Pipeline] Successfully generated and stored {len(saved_ideas)} ideas!")
        return saved_ideas

    except json.JSONDecodeError as e:
        logger.error(f"❌ [Agent Pipeline] Failed to parse JSON from LLM: {raw_content}")
        return []
    except Exception as e:
        logger.error(f"❌ [Agent Pipeline] Error during execution: {str(e)}")
        return []


# --- TEST RUNNER (ISOLATED AGENT TEST) ---
if __name__ == "__main__":
    print("🧪 Testing Autonomous Agent Ideator Pipeline...\n")
    
    # Pastikan DB siap
    db.init_db()
    
    # Test topik
    test_topic = "Artificial Intelligence Indonesia"
    results = generate_viral_ideas(topic=test_topic, num_ideas=2)
    
    print("\n================ HASIL IDE KONTEN VIRAL (V2.0) ================")
    for idx, idea in enumerate(results, start=1):
        print(f"\n💡 IDE #{idx} (DB ID: {idea['id']})")
        print(f"🔥 HOOK        : {idea['hook']}")
        print(f"📌 KONSEP      : {idea['concept']}")
        print(f"🔗 REFERENSI   : {idea['source_links']}")
        print("-" * 60)