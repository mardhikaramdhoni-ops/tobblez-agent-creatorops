from fastapi import APIRouter, HTTPException, status
from app.api.schemas.payloads import AuditRequest, AuditResponse
from app.services.agent import audit_script_async
from app.db.database import save_audit_result

router = APIRouter()

@router.post("/", response_model=AuditResponse, status_code=status.HTTP_200_OK)
async def audit_script_endpoint(payload: AuditRequest):
    try:
        report = await audit_script_async(
            script_text=payload.script_text,
            platform=payload.platform
        )
        
        is_saved = save_audit_result(
            platform=payload.platform,
            script_text=payload.script_text,
            audit_result=report
        )
        
        return AuditResponse(
            status="success",
            platform=payload.platform,
            audit_report=report,
            saved_to_db=is_saved
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kegagalan saat audit: {str(e)}"
        )