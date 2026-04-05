# Azure Deployment Guide — Project CV-11 Plant Disease Detection

---

## Azure Services for Plant Disease Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                              | What it does                                                                 | When to use                                        |
|--------------------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Azure Custom Vision**              | Train custom plant disease classifier on PlantVillage — no code needed       | Replace your ResNet18 fine-tuning pipeline         |
| **Azure Machine Learning**           | Fine-tune ResNet18/EfficientNet on PlantVillage with managed GPU compute     | When you need full control over training           |
| **Azure OpenAI Vision**              | GPT-4V for plant disease identification via prompt                           | When you need zero-shot disease identification     |

> **Azure Custom Vision** trained on PlantVillage is the direct replacement for your ResNet18 fine-tuning pipeline. Upload labelled images → train → deploy endpoint — no code needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                        | What it does                                                        | When to use                                           |
|--------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Container Apps**       | Run your 3 Docker containers (frontend, backend, cv-service)        | Best match for your current microservice architecture |
| **Azure Container Registry**   | Store your Docker images                                            | Used with Container Apps or AKS                       |

### 3. Train and Manage Your Model

| Service                        | What it does                                                              | When to use                                           |
|--------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------|
| **Azure Custom Vision**        | Train custom image classifier via UI — no code needed                     | Quick custom classifier without ML expertise          |
| **Azure Machine Learning**     | Fine-tune ResNet18 on PlantVillage, track experiments, deploy endpoints   | Full ML pipeline for plant disease classification     |

### 4. Frontend Hosting

| Service                   | What it does                                                               |
|---------------------------|----------------------------------------------------------------------------|
| **Azure Static Web Apps** | Host your React frontend — free tier available, auto CI/CD from GitHub     |

### 5. Supporting Services

| Service                       | Purpose                                                                  |
|-------------------------------|--------------------------------------------------------------------------|
| **Azure Blob Storage**        | Store PlantVillage dataset, model weights, and detection results         |
| **Azure Key Vault**           | Store API keys and connection strings instead of .env files              |
| **Azure Monitor + App Insights** | Track detection latency, disease distributions, request volume       |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Azure Static Web Apps — React Frontend                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  Azure Container Apps — Backend (FastAPI :8000)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ Container Apps    │    │ Azure Custom Vision                │
│ CV Service :8001  │    │ Trained on PlantVillage            │
│ PyTorch ResNet18  │    │ No GPU training needed             │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
az login
az group create --name rg-plant-disease --location uksouth
az extension add --name containerapp --upgrade
```

---

## Step 1 — Create Container Registry and Push Images

```bash
az acr create --resource-group rg-plant-disease --name plantdiseaseacr --sku Basic --admin-enabled true
az acr login --name plantdiseaseacr
ACR=plantdiseaseacr.azurecr.io
docker build -f docker/Dockerfile.cv-service -t $ACR/cv-service:latest ./cv-service
docker push $ACR/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ACR/backend:latest ./backend
docker push $ACR/backend:latest
```

---

## Step 2 — Upload Model to Blob Storage

```bash
az storage account create --name plantdiseasemodels --resource-group rg-plant-disease --sku Standard_LRS
az storage container create --name models --account-name plantdiseasemodels
az storage blob upload --account-name plantdiseasemodels --container-name models \
  --name plant_disease_resnet.pth --file cv-service/models/plant_disease_resnet.pth
```

---

## Step 3 — Deploy Container Apps

```bash
az containerapp env create --name plantdisease-env --resource-group rg-plant-disease --location uksouth

az containerapp create \
  --name cv-service --resource-group rg-plant-disease \
  --environment plantdisease-env --image $ACR/cv-service:latest \
  --registry-server $ACR --target-port 8001 --ingress internal \
  --min-replicas 1 --max-replicas 3 --cpu 1 --memory 2.0Gi

az containerapp create \
  --name backend --resource-group rg-plant-disease \
  --environment plantdisease-env --image $ACR/backend:latest \
  --registry-server $ACR --target-port 8000 --ingress external \
  --min-replicas 1 --max-replicas 5 --cpu 0.5 --memory 1.0Gi \
  --env-vars CV_SERVICE_URL=http://cv-service:8001
```

---

## Option B — Use Azure Custom Vision

```python
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

credentials = ApiKeyCredentials(in_headers={"Prediction-key": os.getenv("CUSTOM_VISION_KEY")})
predictor = CustomVisionPredictionClient(os.getenv("CUSTOM_VISION_ENDPOINT"), credentials)

def classify_plant(image_bytes: bytes) -> dict:
    result = predictor.classify_image(
        project_id=os.getenv("CUSTOM_VISION_PROJECT_ID"),
        published_name="production",
        image_data=image_bytes
    )
    top = result.predictions[0]
    return {
        "label": top.tag_name,
        "confidence": round(top.probability * 100, 2),
        "top3": [{"label": p.tag_name, "confidence": round(p.probability * 100, 2)} for p in result.predictions[:3]]
    }
```

---

## Estimated Monthly Cost

| Service                  | Tier      | Est. Cost         |
|--------------------------|-----------|-------------------|
| Container Apps (backend) | 0.5 vCPU  | ~$10–15/month     |
| Container Apps (cv-svc)  | 1 vCPU    | ~$15–20/month     |
| Container Registry       | Basic     | ~$5/month         |
| Static Web Apps          | Free      | $0                |
| Azure Custom Vision      | S0 tier   | Pay per prediction|
| **Total (Option A)**     |           | **~$30–40/month** |
| **Total (Option B)**     |           | **~$15–25/month** |

For exact estimates → https://calculator.azure.com

---

## Teardown

```bash
az group delete --name rg-plant-disease --yes --no-wait
```
