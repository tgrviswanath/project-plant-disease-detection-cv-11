# Project 11 - Plant Disease Detection (CV)

Classify plant leaf diseases using a fine-tuned ResNet18 on PlantVillage dataset (38 classes).

## Architecture

```
Frontend :3000  →  Backend :8000  →  CV Service :8001
  React/MUI        FastAPI/httpx      FastAPI/PyTorch ResNet18
```

## 38 Disease Classes (PlantVillage)
Covers: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato,
Raspberry, Soybean, Squash, Strawberry, Tomato — healthy + disease variants.

## What's New vs Previous Projects

| | P06-P10 | P11 |
|---|---|---|
| Model | Pretrained (no training) | Custom trained ResNet18 |
| Training | Not required | Required (`train.py`) |
| Dataset | COCO / MediaPipe built-in | PlantVillage (38 classes) |
| New concept | Inference only | Transfer learning + fine-tuning |

## Local Run

```bash
# Terminal 1 - CV Service (train model first)
cd cv-service && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python train.py          # ~5-10 min on CPU, creates models/plant_disease_resnet.pth
uvicorn app.main:app --reload --port 8001

# Terminal 2 - Backend
cd backend && python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3 - Frontend
cd frontend && npm install && npm start
```

## Real Dataset
Download PlantVillage from Kaggle:
https://www.kaggle.com/datasets/emmarex/plantdisease

Place in: `cv-service/data/plantvillage/train/` and `cv-service/data/plantvillage/val/`

## Docker
```bash
docker-compose up --build
```
