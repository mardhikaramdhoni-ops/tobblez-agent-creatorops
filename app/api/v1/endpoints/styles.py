from fastapi import APIRouter, HTTPException, status
from app.api.schemas.payloads import StyleAddRequest, StyleQueryRequest, StyleResponse
from app.db.vector_store import add_style_sample, query_style

router = APIRouter()

@router.post(
    "/add", 
    response_model=StyleResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Contoh Gaya Bahasa ke ChromaDB"
)
async def add_style_endpoint(payload: StyleAddRequest):
    try:
        doc_id = add_style_sample(
            text=payload.text,
            category=payload.category,
            custom_id=payload.custom_id
        )
        return StyleResponse(
            status="success",
            message="Contoh gaya bahasa berhasil disimpan ke Vector Store (ChromaDB).",
            data={"id": doc_id, "category": payload.category}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal menambahkan style ke ChromaDB: {str(e)}"
        )

@router.post(
    "/query", 
    response_model=StyleResponse, 
    status_code=status.HTTP_200_OK,
    summary="Cari Referensi Gaya Bahasa Serupa"
)
async def query_style_endpoint(payload: StyleQueryRequest):
    try:
        results = query_style(
            query_text=payload.query_text,
            n_results=payload.n_results
        )
        return StyleResponse(
            status="success",
            message="Berhasil mengambil referensi style dari ChromaDB.",
            data={"matched_styles": results}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal melakukan similarity search: {str(e)}"
        )