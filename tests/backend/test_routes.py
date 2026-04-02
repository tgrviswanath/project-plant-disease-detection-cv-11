from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "label": "Tomato___healthy", "plant": "Tomato", "disease": "healthy",
    "is_healthy": True, "confidence": 92.5,
    "top5": [{"label": "Tomato___healthy", "confidence": 92.5, "plant": "Tomato",
               "disease": "healthy", "is_healthy": True}],
}


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


@patch("app.core.service.predict_disease", new_callable=AsyncMock, return_value=MOCK_RESULT)
def test_predict_endpoint(mock_pred):
    r = client.post("/api/v1/predict",
        files={"file": ("leaf.jpg", b"fake", "image/jpeg")})
    assert r.status_code == 200
    assert r.json()["is_healthy"] is True
    assert r.json()["plant"] == "Tomato"
