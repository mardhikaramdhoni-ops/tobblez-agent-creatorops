import chromadb
from config import settings

# Inisialisasi Client ChromaDB (Persistent)
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)

# Buat collection (kayak tabel di SQL tapi buat vector)
# Kita kasih nama 'creator_style'
collection = chroma_client.get_or_create_collection(name="creator_style")

def add_style_example(content, metadata):
    """
    Nambahin contoh gaya konten lu ke database
    """
    # Di V1 ini, kita biarin ChromaDB pake embedding bawaan (Default)
    # Nanti di V-selanjutnya kita bisa upgrade pake HuggingFace/OpenAI embedding
    def datetime_now():
        ...

    collection.add(
        documents=[content],
        metadatas=[metadata],
        ids=[f"id_{datetime_now()}"] # Pake timestamp atau string unik
    )
    print("✨ Gaya konten berhasil ditambahin ke Vector Store!")

def query_style(query_text):
    """
    Nyari contoh gaya konten yang paling mirip sama draf lu
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=1
    )
    return results['documents'][0] if results['documents'] else []

if __name__ == "__main__":
    # Test input gaya konten lu
    import time
    
    # Kita masukin contoh gaya konten "Tobblez Style"
    sample_style = "Gaya Tobblez: Pake bahasa santai (lu/gw), teknis banget, to the point, dan selalu ada bumbu MLOps-nya."
    
    collection.add(
        documents=[sample_style],
        metadatas=[{"category": "personality"}],
        ids=["style_1"]
    )
    
    print("✅ ChromaDB Ready & Style Added!")
    
    # Test Query
    res = query_style("Gimana cara ngomong yang santai?")
    print(f"Hasil pencarian gaya: {res}")