"""
Plant disease classifier using fine-tuned ResNet18.
- Model trained on PlantVillage dataset (38 classes)
- Run train.py first to generate models/plant_disease_resnet.pth
"""
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import os
from app.core.config import settings
from app.core.labels import CLASSES, parse_label

_model = None

TRANSFORM = transforms.Compose([
    transforms.Resize((settings.IMAGE_SIZE, settings.IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def _get_model():
    global _model
    if _model is None:
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run: python train.py inside cv-service/"
            )
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, settings.NUM_CLASSES)
        model.load_state_dict(torch.load(settings.MODEL_PATH, map_location="cpu"))
        model.eval()
        _model = model
    return _model


def predict(image_bytes: bytes) -> dict:
    model = _get_model()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = TRANSFORM(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]

    top5_idx = probs.topk(5).indices.tolist()
    top5 = [
        {
            "label": CLASSES[i],
            "confidence": round(float(probs[i]) * 100, 2),
            **parse_label(CLASSES[i]),
        }
        for i in top5_idx
    ]

    top = top5[0]
    return {
        "label": top["label"],
        "plant": top["plant"],
        "disease": top["disease"],
        "is_healthy": top["is_healthy"],
        "confidence": top["confidence"],
        "top5": top5,
    }
