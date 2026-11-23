"""
vector_store.py - ChromaDB Vector Store Layer for CreatorOps AI Agent
Stores and retrieves writing styles & creator personas.
"""
import logging
import chromadb
from typing import List

# Setup Logger
logger = logging.getLogger("CreatorOps.VectorStore")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Persistent ChromaDB Client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="creator_style")


def add_style_sample(text: str, style_name: str = "default_persona"):
    """Menyimpan sampel gaya penulisan ke ChromaDB."""
    try:
        # Pake hash/length sederhana buat ID
        doc_id = f"style_{hash(text)}"
        collection.add(
            documents=[text],
            metadatas=[{"style_name": style_name}],
            ids=[doc_id]
        )
        logger.info(f"💾 Added style sample to ChromaDB (ID: {doc_id})")
    except Exception as e:
        logger.error(f"❌ Error adding style to ChromaDB: {str(e)}")


def search_similar_styles(query: str, n_results: int = 2) -> str:
    """
    Mencari sampel gaya penulisan yang mirip berdasarkan query topik.
    """
    logger.info(f"🔍 [VectorStore] Querying styles for: '{query}'")
    try:
        count = collection.count()
        if count == 0:
            logger.warning("⚠️ ChromaDB collection is empty! Returning default style fallback.")
            return "Gaya penulisan: Kasual, santai, to-the-point, edukatif, dan menarik perhatian anak muda/tech enthusiast."

        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        
        documents = results.get("documents", [[]])[0]
        if not documents:
            return "Gaya penulisan: Kasual, santai, to-the-point, edukatif."
            
        return "\n---\n".join(documents)

    except Exception as e:
        logger.error(f"❌ Error retrieving style from ChromaDB: {str(e)}")
        return "Gaya penulisan: Kasual, santai, to-the-point, edukatif."


# --- TEST RUNNER (ISOLATED TEST) ---
if __name__ == "__main__":
    print("🧪 Testing Vector Store...")
    # Seed data jika kosong
    add_style_sample("Gaya penulisan gw itu santai, pake bahasa 'lu/gw', pembukaan pake HOOK yang bikin penasaran, dan penutupan selalu ngajak diskusi.")
    
    res = search_similar_styles("AI trends")
    print("\n--- RETRIEVED STYLE ---")
    print(res)