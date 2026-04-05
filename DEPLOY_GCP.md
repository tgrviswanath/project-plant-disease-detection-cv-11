# GCP Deployment Guide — Project CV-11 Plant Disease Detection

---

## GCP Services for Plant Disease Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Vertex AI AutoML Vision**          | Train custom plant disease classifier on PlantVillage — no code needed       | Replace your ResNet18 fine-tuning pipeline         |
| **Vertex AI**                        | Fine-tune ResNet18/EfficientNet on PlantVillage with managed GPU compute     | When you need full control over training           |
| **Vertex AI Gemini Vision**          | Gemini Pro Vision for plant disease identification via prompt                | When you need zero-shot disease identification     |

> **Vertex AI AutoML Vision** trained on PlantVillage is the direct replacement for your ResNet18 fine-tuning pipeline. Upload labelled images → train → deploy endpoint — no code needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Cloud Run**              | Run backend + cv-service containers — serverless, scales to zero    | Best match for your current microservice architecture |
| **Artifact Registry**      | Store your Docker images                                            | Used with Cloud Run or GKE                            |

### 3. Frontend Hosting

| Service                    | What it does                                                              |
|----------------------------|---------------------------------------------------------------------------| 
| **Firebase Hosting**       | Host your React frontend — free tier, auto CI/CD from GitHub              |

### 4. Supporting Services

| Service                        | Purpose                                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| **Cloud Storage**              | Store PlantVillage dataset, model weights, and detection results          |
| **Secret Manager**             | Store API keys and connection strings instead of .env files               |
| **Cloud Monitoring + Logging** | Track detection latency, disease distributions, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Firebase Hosting — React Frontend                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Cloud Run — Backend (FastAPI :8000)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal HTTPS
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Cloud Run         │    │ Vertex AI AutoML Vision            │
│ CV Service :8001  │    │ Trained on PlantVillage            │
│ PyTorch ResNet18  │    │ No GPU training needed             │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
gcloud auth login
gcloud projects create plantdisease-cv-project --name="Plant Disease Detection"
gcloud config set project plantdisease-cv-project
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com \
  storage.googleapis.com cloudbuild.googleapis.com
```

---

## Step 1 — Create Artifact Registry and Push Images

```bash
GCP_REGION=europe-west2
gcloud artifacts repositories create plantdisease-repo \
  --repository-format=docker --location=$GCP_REGION
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev
AR=$GCP_REGION-docker.pkg.dev/plantdisease-cv-project/plantdisease-repo
docker build -f docker/Dockerfile.cv-service -t $AR/cv-service:latest ./cv-service
docker push $AR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $AR/backend:latest ./backend
docker push $AR/backend:latest
```

---

## Step 2 — Upload Model to Cloud Storage

```bash
gsutil mb -l $GCP_REGION gs://plantdisease-models-plantdisease-cv-project
gsutil cp cv-service/models/plant_disease_resnet.pth gs://plantdisease-models-plantdisease-cv-project/models/
```

---

## Step 3 — Deploy to Cloud Run

```bash
gcloud run deploy cv-service \
  --image $AR/cv-service:latest --region $GCP_REGION \
  --port 8001 --no-allow-unauthenticated \
  --min-instances 1 --max-instances 3 --memory 2Gi --cpu 1

CV_URL=$(gcloud run services describe cv-service --region $GCP_REGION --format "value(status.url)")

gcloud run deploy backend \
  --image $AR/backend:latest --region $GCP_REGION \
  --port 8000 --allow-unauthenticated \
  --min-instances 1 --max-instances 5 --memory 1Gi --cpu 1 \
  --set-env-vars CV_SERVICE_URL=$CV_URL
```

---

## Option B — Use Vertex AI AutoML Vision

```python
from google.cloud import aiplatform

aiplatform.init(project="plantdisease-cv-project", location="europe-west2")
endpoint = aiplatform.Endpoint("projects/plantdisease-cv-project/locations/europe-west2/endpoints/<endpoint-id>")

def classify_plant(image_bytes: bytes) -> dict:
    import base64
    instances = [{"content": base64.b64encode(image_bytes).decode()}]
    prediction = endpoint.predict(instances=instances)
    result = prediction.predictions[0]
    labels = result.get("displayNames", [])
    confidences = result.get("confidences", [])
    if not labels:
        return {"label": "unknown", "confidence": 0, "top3": []}
    top_idx = confidences.index(max(confidences))
    return {
        "label": labels[top_idx],
        "confidence": round(confidences[top_idx] * 100, 2),
        "top3": [{"label": labels[i], "confidence": round(confidences[i] * 100, 2)} for i in range(min(3, len(labels)))]
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier                  | Est. Cost          |
|----------------------------|-----------------------|--------------------|
| Cloud Run (backend)        | 1 vCPU / 1 GB         | ~$10–15/month      |
| Cloud Run (cv-service)     | 1 vCPU / 2 GB         | ~$12–18/month      |
| Artifact Registry          | Storage               | ~$1–2/month        |
| Firebase Hosting           | Free tier             | $0                 |
| Cloud Storage (models)     | Standard              | ~$1/month          |
| Vertex AI AutoML           | Pay per node hour     | Pay per use        |
| **Total (Option A)**       |                       | **~$24–36/month**  |
| **Total (Option B)**       |                       | **~$12–18/month + training cost** |

For exact estimates → https://cloud.google.com/products/calculator

---

## Teardown

```bash
gcloud run services delete backend --region $GCP_REGION --quiet
gcloud run services delete cv-service --region $GCP_REGION --quiet
gcloud artifacts repositories delete plantdisease-repo --location=$GCP_REGION --quiet
gsutil rm -r gs://plantdisease-models-plantdisease-cv-project
gcloud projects delete plantdisease-cv-project
```
