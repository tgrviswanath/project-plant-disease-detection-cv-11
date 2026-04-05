# Project CV-11 - Plant Disease Detection

Microservice CV system that classifies plant leaf diseases using a fine-tuned ResNet18 on PlantVillage dataset (38 classes).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND  (React - Port 3000)                              │
│  axios POST /api/v1/classify                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  BACKEND  (FastAPI - Port 8000)                             │
│  httpx POST /api/v1/cv/classify  →  calls cv-service        │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP JSON
┌──────────────────────▼──────────────────────────────────────┐
│  CV SERVICE  (FastAPI - Port 8001)                          │
│  Loads plant_disease_resnet.pth                             │
│  ResNet18 inference → disease label + confidence            │
│  Returns { label, confidence, top3, plant, condition }      │
└─────────────────────────────────────────────────────────────┘
```

---

## 38 Disease Classes (PlantVillage)

Covers: Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato — healthy + disease variants.

---

## What's New vs Previous Projects

| | CV-01 to CV-10 | CV-11 |
|---|---|---|
| Model | Pretrained (no training) | Custom trained ResNet18 |
| Training | Not required | Required (`train.py`) |
| Dataset | COCO / MediaPipe built-in | PlantVillage (38 classes) |
| New concept | Inference only | Transfer learning + fine-tuning |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Frontend | React, MUI |
| Backend | FastAPI, httpx |
| CV | PyTorch, torchvision (ResNet18), Pillow |
| Dataset | PlantVillage (38 classes) |
| Deployment | Docker, docker-compose |

---

## Prerequisites

- Python 3.12+
- Node.js — run `nvs use 20.14.0` before starting the frontend

---

## Local Run

### Step 1 — Download Dataset

```
Download PlantVillage from Kaggle:
https://www.kaggle.com/datasets/emmarex/plantdisease

Place in: cv-service/data/plantvillage/train/ and cv-service/data/plantvillage/val/
```

### Step 2 — Train the CV model (run once)

```bash
cd cv-service
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
python train.py
# ~5-10 min on CPU, creates models/plant_disease_resnet.pth
```

### Step 3 — Start CV Service (Terminal 1)

```bash
cd cv-service
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

Verify: http://localhost:8001/health → `{"status":"ok"}`

### Step 4 — Start Backend (Terminal 2)

```bash
cd backend
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Step 5 — Start Frontend (Terminal 3)

```bash
cd frontend
npm install && npm start
```

Opens at: http://localhost:3000

---

## Environment Files

### `backend/.env`

```
APP_NAME=Plant Disease Detection API
APP_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
CV_SERVICE_URL=http://localhost:8001
```

### `frontend/.env`

```
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Run

```bash
# Train model first
cd cv-service && python train.py
cd ..
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |
| CV Service docs | http://localhost:8001/docs |

---

## Run Tests

```bash
cd cv-service && venv\Scripts\activate
pytest ../tests/cv-service/ -v

cd backend && venv\Scripts\activate
pytest ../tests/backend/ -v
```

---

## Project Structure

```
project-plant-disease-detection-cv-11/
├── frontend/                    ← React (Port 3000)
├── backend/                     ← FastAPI (Port 8000)
├── cv-service/                  ← FastAPI CV (Port 8001)
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/classifier.py   ← ResNet18 inference
│   │   └── main.py
│   ├── data/plantvillage/       ← dataset (download separately)
│   ├── models/                  ← plant_disease_resnet.pth (after train.py)
│   └── train.py                 ← run once to generate model
├── samples/
├── tests/
├── docker/
└── docker-compose.yml
```

---

## API Reference

```
POST /api/v1/classify
Body:     { "image": "<base64>" }
Response: {
  "label": "Tomato___Late_blight",
  "plant": "Tomato",
  "condition": "Late blight",
  "confidence": 94.7,
  "top3": [{ "label": "...", "confidence": ... }]
}
```
