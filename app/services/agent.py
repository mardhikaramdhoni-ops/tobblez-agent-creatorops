"""
agent.py - Realtime Async Streaming Agent for CreatorOps V4.0 (Bulletproof)
"""
import asyncio
from typing import AsyncGenerator
from groq import AsyncGroq
from app.core.config import settings
from app.services.tools import search_web, format_search_results_for_llm
from app.db.vector_store import search_similar_styles, query_style

# Inisialisasi Async Client Groq
groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


async def stream_generate_ideas(topic: str) -> AsyncGenerator[str, None]:
    """
    Async Generator yang aman dan tahan banting.
    Mengirim stream token ke SSE. Jika ada error, dikirim sebagai teks ke layar.
    """
    try:
        # 1. Non-blocking I/O: Ambil Tren & RAG Persona Style (dengan fallback aman)
        try:
            raw_news = await asyncio.to_thread(search_web, topic, 3, "id")
            news_data = format_search_results_for_llm(raw_news)
        except Exception as e:
            news_data = f"(Pencarian web dilewati: {str(e)})"

        try:
            style_context = await asyncio.to_thread(search_similar_styles, topic, 2)
        except Exception as e:
            style_context = "(Gaya default kreator)"

        system_prompt = f"""
Lu adalah AI Content Strategist handal (CreatorOps V4.0).

[GAYA PENULISAN / CREATOR PERSONA]
{style_context}

[RISET TREN TERKINI]
{news_data}

TUGAS:
Buat 3 Ide Konten Viral berdasarkan topik '{topic}'.
Gunakan format Markdown yang rapi:
- Judul / Hook Menarik
- Angle Konten & Target Audiens
- Struktur Singkat (Hook, Body, Call to Action)
"""

        # Pastikan nama model valid (Gunakan fallback jika salah satu None)
        model_name = getattr(settings, "GROQ_MODEL", None) or getattr(settings, "LLM_MODEL", "llama-3.3-70b-versatile")

        # 2. Panggil Groq LLM secara Realtime Streaming
        response_stream = await groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Bikinin ide konten viral untuk topik: {topic}"}
            ],
            temperature=0.7,
            stream=True
        )

        # 3. Stream token per token langsung ke client
        async for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    except Exception as err:
        # JIKA TERJADI ERROR, JANGAN CRASH! Kirim errornya ke terminal CRT browser!
        yield f"\n\n🚨 [SYSTEM ENGINE ERROR]: {str(err)}\nPastikan GROQ_API_KEY valid dan kuota mencukupi."


async def audit_script_async(script_text: str, platform: str) -> str:
    # ... fungsi audit_script_async lu tetap sama ...
    style_context = query_style(query_text=script_text[:120], n_results=2)
    
    system_prompt = (
        "Kamu adalah Senior Content Director & Script Doctor yang jujur, tajam, dan objektif.\n"
        f"Referensi Gaya Bahasa Kreator:\n{style_context}\n\n"
        "Audit naskah yang diberikan untuk platform yang ditentukan.\n"
        "Berikan output berformat Markdown dengan poin:\n"
        "1. **Skor Naskah (1-100)** + Evaluasi singkat.\n"
        "2. **Analisis Hook (3 Detik Pertama):** Nendang atau garing?\n"
        "3. **Pacing & Retensi:** Bagian mana yang bertele-tele dan harus di-cut?\n"
        "4. **Kesesuaian Tone:** Apakah sudah sesuai dengan persona/gaya bahasa kreator?\n"
        "5. **Naskah Final Siap Rekam:** Tulis ulang versi naskah yang sudah diperbaiki secara actionable!"
    )

    user_prompt = f"Target Platform: {platform}\n\nDraf Naskah:\n\"\"\"\n{script_text}\n\"\"\""

    model_name = getattr(settings, "LLM_MODEL", None) or getattr(settings, "GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        response = await groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            max_tokens=2048,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"LLM Audit Error: {str(e)}")