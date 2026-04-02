from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.service import predict_disease
import httpx

router = APIRouter(prefix="/api/v1", tags=["plant-disease"])


def _handle(e):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="CV service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        content = await file.read()
        return await predict_disease(file.filename, content, file.content_type or "image/jpeg")
    except Exception as e:
        _handle(e)
