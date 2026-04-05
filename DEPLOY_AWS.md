# AWS Deployment Guide — Project CV-11 Plant Disease Detection

---

## AWS Services for Plant Disease Detection

### 1. Ready-to-Use AI (No Model Needed)

| Service                    | What it does                                                                 | When to use                                        |
|----------------------------|------------------------------------------------------------------------------|----------------------------------------------------|
| **Amazon Rekognition Custom** | Train custom plant disease classifier on PlantVillage dataset             | Replace your ResNet18 fine-tuning pipeline         |
| **AWS SageMaker JumpStart** | One-click fine-tune ResNet/EfficientNet on PlantVillage — managed GPU      | When you need managed transfer learning            |
| **Amazon Bedrock**         | Claude Vision for plant disease identification via prompt                    | When you need zero-shot disease identification     |

> **Amazon Rekognition Custom Labels** trained on PlantVillage is the direct replacement for your ResNet18 fine-tuning pipeline. Upload labelled images → train → deploy endpoint — no code needed.

### 2. Host Your Own Model (Keep Current Stack)

| Service                    | What it does                                                        | When to use                                           |
|----------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS App Runner**         | Run backend container — simplest, no VPC or cluster needed          | Quickest path to production                           |
| **Amazon ECS Fargate**     | Run backend + cv-service containers in a private VPC                | Best match for your current microservice architecture |
| **Amazon ECR**             | Store your Docker images                                            | Used with App Runner, ECS, or EKS                     |

### 3. Train and Manage Your Model

| Service                         | What it does                                                        | When to use                                           |
|---------------------------------|---------------------------------------------------------------------|-------------------------------------------------------|
| **AWS SageMaker**               | Fine-tune ResNet18 on PlantVillage, track experiments, deploy       | Full ML pipeline for plant disease classification     |
| **Amazon S3**                   | Store PlantVillage dataset and trained model weights                | Dataset and model artifact storage                    |

### 4. Frontend Hosting

| Service               | What it does                                                                  |
|-----------------------|-------------------------------------------------------------------------------|
| **Amazon S3**         | Host your React build as a static website                                     |
| **Amazon CloudFront** | CDN in front of S3 — HTTPS, low latency globally                              |

### 5. Supporting Services

| Service                  | Purpose                                                                   |
|--------------------------|---------------------------------------------------------------------------|
| **Amazon S3**            | Store uploaded plant images and disease detection results                 |
| **AWS Secrets Manager**  | Store API keys and connection strings instead of .env files               |
| **Amazon CloudWatch**    | Track detection latency, disease distributions, request volume            |

---

## Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  S3 + CloudFront — React Frontend                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────────────┐
│  AWS App Runner / ECS Fargate — Backend (FastAPI :8000)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Internal
        ┌──────────────┴──────────────┐
        │ Option A                    │ Option B
        ▼                             ▼
┌───────────────────┐    ┌────────────────────────────────────┐
│ ECS Fargate       │    │ Amazon Rekognition Custom Labels   │
│ CV Service :8001  │    │ Trained on PlantVillage            │
│ PyTorch ResNet18  │    │ No GPU training needed             │
└───────────────────┘    └────────────────────────────────────┘
```

---

## Prerequisites

```bash
aws configure
AWS_REGION=eu-west-2
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

---

## Step 1 — Create ECR and Push Images

```bash
aws ecr create-repository --repository-name plantdisease/cv-service --region $AWS_REGION
aws ecr create-repository --repository-name plantdisease/backend --region $AWS_REGION
ECR=$AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR
docker build -f docker/Dockerfile.cv-service -t $ECR/plantdisease/cv-service:latest ./cv-service
docker push $ECR/plantdisease/cv-service:latest
docker build -f docker/Dockerfile.backend -t $ECR/plantdisease/backend:latest ./backend
docker push $ECR/plantdisease/backend:latest
```

---

## Step 2 — Upload Model to S3

```bash
aws s3 mb s3://plantdisease-models-$AWS_ACCOUNT --region $AWS_REGION
aws s3 cp cv-service/models/plant_disease_resnet.pth s3://plantdisease-models-$AWS_ACCOUNT/models/
```

---

## Step 3 — Deploy with App Runner

```bash
aws apprunner create-service \
  --service-name plantdisease-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "'$ECR'/plantdisease/backend:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "CV_SERVICE_URL": "http://cv-service:8001"
        }
      }
    }
  }' \
  --instance-configuration '{"Cpu": "1 vCPU", "Memory": "2 GB"}' \
  --region $AWS_REGION
```

---

## Option B — Use Amazon Rekognition Custom Labels

```python
import boto3

rekognition = boto3.client("rekognition", region_name="eu-west-2")

def classify_plant(image_bytes: bytes) -> dict:
    response = rekognition.detect_custom_labels(
        ProjectVersionArn="arn:aws:rekognition:eu-west-2:<account>:project/plant-disease/version/plant-disease.2024/1234567890",
        Image={"Bytes": image_bytes},
        MinConfidence=50
    )
    labels = response["CustomLabels"]
    if not labels:
        return {"label": "unknown", "confidence": 0, "top3": []}
    top = labels[0]
    return {
        "label": top["Name"],
        "confidence": round(top["Confidence"], 2),
        "top3": [{"label": l["Name"], "confidence": round(l["Confidence"], 2)} for l in labels[:3]]
    }
```

---

## Estimated Monthly Cost

| Service                    | Tier              | Est. Cost          |
|----------------------------|-------------------|--------------------|
| App Runner (backend)       | 1 vCPU / 2 GB     | ~$20–25/month      |
| App Runner (cv-service)    | 1 vCPU / 2 GB     | ~$20–25/month      |
| ECR + S3 + CloudFront      | Standard          | ~$3–7/month        |
| Rekognition Custom Labels  | Pay per image     | ~$4/1000 images    |
| **Total (Option A)**       |                   | **~$43–57/month**  |
| **Total (Option B)**       |                   | **~$23–32/month**  |

For exact estimates → https://calculator.aws

---

## Teardown

```bash
aws ecr delete-repository --repository-name plantdisease/backend --force
aws ecr delete-repository --repository-name plantdisease/cv-service --force
aws s3 rm s3://plantdisease-models-$AWS_ACCOUNT --recursive
aws s3 rb s3://plantdisease-models-$AWS_ACCOUNT
```
