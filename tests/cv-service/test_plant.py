from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from PIL import Image
import io
from app.main import app

client = TestClient(app)


def _sample_image() -> bytes:
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


MOCK_RESULT = {
    "label": "Tomato___healthy",
    "plant": "Tomato",
    "disease": "healthy",
    "is_healthy": True,
    "confidence": 92.5,
    "top5": [
        {"label": "Tomato___healthy", "confidence": 92.5, "plant": "Tomato", "disease": "healthy", "is_healthy": True},
        {"label": "Tomato___Early_blight", "confidence": 4.2, "plant": "Tomato", "disease": "Early blight", "is_healthy": False},
    ],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.classifier.predict", return_value=MOCK_RESULT)
def test_predict(mock_pred):
    r = client.post("/api/v1/cv/predict",
        files={"file": ("leaf.jpg", _sample_image(), "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert data["is_healthy"] is True
    assert data["plant"] == "Tomato"
    assert data["confidence"] == 92.5


def test_unsupported_format():
    r = client.post("/api/v1/cv/predict",
        files={"file": ("test.gif", b"GIF89a", "image/gif")})
    assert r.status_code == 400


def test_empty_file():
    r = client.post("/api/v1/cv/predict",
        files={"file": ("leaf.jpg", b"", "image/jpeg")})
    assert r.status_code == 400


def test_model_not_found():
    with patch("app.core.classifier._get_model", side_effect=FileNotFoundError("Model not found")):
        r = client.post("/api/v1/cv/predict",
            files={"file": ("leaf.jpg", _sample_image(), "image/jpeg")})
        assert r.status_code == 503
