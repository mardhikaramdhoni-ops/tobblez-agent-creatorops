from pydantic import BaseModel, Field
from typing import Optional, Any

# ==========================================
# 🔍 SCHEMAS UNTUK SCRIPT AUDIT
# ==========================================
class AuditRequest(BaseModel):
    script_text: str = Field(
        ..., 
        min_length=20, 
        description="Teks naskah konten yang mau diaudit (minimal 20 karakter)."
    )
    platform: str = Field(
        default="TikTok / Reels / Shorts",
        description="Target platform konten (misal: YouTube, TikTok, LinkedIn, Instagram)."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "script_text": "Halo bro! Pernah gak lu coding seharian tapi pas di-run error-nya cuma gara-gara typo titik koma? Hari ini gw mau bagi 3 tips debugging anti-stress...",
                "platform": "TikTok"
            }
        }
    }

class AuditResponse(BaseModel):
    status: str = "success"
    platform: str
    audit_report: str
    saved_to_db: bool


# ==========================================
# 🎨 SCHEMAS UNTUK CHROMADB STYLES (RAG)
# ==========================================
class StyleAddRequest(BaseModel):
    text: str = Field(
        ..., 
        min_length=15, 
        description="Contoh kalimat/naskah dengan gaya bahasa khas kreator."
    )
    category: str = Field(
        default="general", 
        description="Kategori tone/style (misal: hook, storytelling, outro, roasting)."
    )
    custom_id: Optional[str] = Field(
        default=None, 
        description="ID opsional. Kalau kosong bakal otomatis pakai UUID."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Jangan ngaku engineer kalau belum pernah ngerasain panik pas server production down jam 3 pagi!",
                "category": "hook",
                "custom_id": "hook_mumi_01"
            }
        }
    }

class StyleQueryRequest(BaseModel):
    query_text: str = Field(..., min_length=3, description="Topik/kata kunci untuk mencari referensi tone.")
    n_results: int = Field(default=2, ge=1, le=5, description="Jumlah referensi yang ditarik dari ChromaDB.")

class StyleResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None