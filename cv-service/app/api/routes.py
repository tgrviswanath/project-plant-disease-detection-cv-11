import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.classifier import predict
from app.core.validate import validate_image

router = APIRouter(prefix="/api/v1/cv", tags=["plant-disease"])


@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    validate_image(file, content)
    try:
        return await asyncio.get_running_loop().run_in_executor(None, predict, content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {e}")
