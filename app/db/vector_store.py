import chromadb
import uuid
from typing import Optional, List
from app.core.config import settings

# 1. Inisialisasi ChromaDB Persistent Client
# Menyimpan embedding vector langsung ke folder lokal (chroma_db/)
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)

# Buat atau ambil koleksi untuk menyimpan gaya bahasa kreator
collection = chroma_client.get_or_create_collection(
    name="creator_styles",
    metadata={"description": "Koleksi gaya bahasa & tone naskah khas Tobblez"}
)

def add_style_sample(text: str, category: str = "general", custom_id: Optional[str] = None) -> str:
    """
    Menambahkan contoh gaya bahasa baru ke ChromaDB.
    """
    doc_id = custom_id if custom_id else str(uuid.uuid4())
    
    collection.add(
        documents=[text],
        metadatas=[{"category": category}],
        ids=[doc_id]
    )
    return doc_id

def query_style(query_text: str, n_results: int = 2) -> str:
    """
    Melakukan Semantic Similarity Search ke ChromaDB untuk mengambil
    referensi gaya bahasa yang paling relevan dengan topik naskah.
    """
    try:
        # Cek apakah koleksi ada isinya
        count = collection.count()
        if count == 0:
            return "Tone Default: Santai, to-the-point, teknis tapi mudah dipahami (lu/gw), berstandar Senior Engineer."

        # Ambil n_results, tapi jangan melebihi total data yang ada
        actual_n = min(n_results, count)

        results = collection.query(
            query_texts=[query_text],
            n_results=actual_n
        )

        documents = results.get("documents", [[]])[0]
        if not documents:
            return "Tone Default: Santai, to-the-point, edukatif."

        # Format hasil jadi teks referensi rapi untuk prompt AI
        formatted_context = "\n".join([f"- \"{doc}\"" for doc in documents])
        return formatted_context

    except Exception as e:
        print(f"[VECTOR DB WARNING] Gagal query ChromaDB: {e}")
        return "Tone Default: Santai, to-the-point, edukatif."

        # Alias untuk backward-compatibility dengan agent.py versi sebelumnya
search_similar_styles = query_style