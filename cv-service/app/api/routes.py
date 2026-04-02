from fastapi import APIRouter, HTTPException, UploadFile, File
from app.core.classifier import predict

router = APIRouter(prefix="/api/v1/cv", tags=["plant-disease"])
ALLOWED = {"jpg", "jpeg", "png", "bmp", "webp"}


def _validate(filename: str):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: .{ext}")


@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    _validate(file.filename)
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        return predict(content)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
