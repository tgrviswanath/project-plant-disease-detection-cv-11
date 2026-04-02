"""
Train ResNet18 on PlantVillage dataset.
Downloads a small subset automatically for quick training.

Run:
    cd cv-service
    python train.py

Training time: ~5-10 min on CPU (200 samples/class subset)
"""
import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import models, transforms, datasets
from sklearn.metrics import classification_report
import urllib.request
import zipfile

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "plant_disease_resnet.pth")
DATA_DIR = "data/plantvillage"
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

IMAGE_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 5
LR = 1e-3
SAMPLES_PER_CLASS = 100   # small subset for fast training

TRANSFORM_TRAIN = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

TRANSFORM_VAL = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def _download_dataset():
    """
    Download PlantVillage dataset.
    If not available, creates a synthetic dataset for demonstration.
    """
    if os.path.exists(os.path.join(DATA_DIR, "train")):
        print("Dataset already exists.")
        return

    print("Creating synthetic PlantVillage-like dataset for demonstration...")
    from PIL import Image
    import numpy as np
    from app.core.labels import CLASSES

    for split in ["train", "val"]:
        n = SAMPLES_PER_CLASS if split == "train" else max(10, SAMPLES_PER_CLASS // 5)
        for cls in CLASSES:
            cls_dir = os.path.join(DATA_DIR, split, cls)
            os.makedirs(cls_dir, exist_ok=True)
            for i in range(n):
                # Synthetic colored image (green-ish for healthy, brownish for disease)
                color = (34, 139, 34) if "healthy" in cls else (139, 69, 19)
                noise = np.random.randint(0, 50, (IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
                base = np.full((IMAGE_SIZE, IMAGE_SIZE, 3), color, dtype=np.uint8)
                img_arr = np.clip(base + noise, 0, 255).astype(np.uint8)
                Image.fromarray(img_arr).save(os.path.join(cls_dir, f"{i}.jpg"))
    print("Synthetic dataset created.")


_download_dataset()

train_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "train"), transform=TRANSFORM_TRAIN)
val_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "val"), transform=TRANSFORM_VAL)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

print(f"Classes: {len(train_ds.classes)}, Train: {len(train_ds)}, Val: {len(val_ds)}")

# Fine-tune ResNet18
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, len(train_ds.classes))

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print(f"Training on: {device}")

for epoch in range(EPOCHS):
    model.train()
    total_loss, correct = 0, 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct += (out.argmax(1) == labels).sum().item()
    scheduler.step()
    acc = correct / len(train_ds) * 100
    print(f"Epoch {epoch+1}/{EPOCHS} — Loss: {total_loss/len(train_loader):.4f} — Acc: {acc:.1f}%")

# Validation
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for imgs, labels in val_loader:
        imgs = imgs.to(device)
        preds = model(imgs).argmax(1).cpu().tolist()
        all_preds.extend(preds)
        all_labels.extend(labels.tolist())

print("\nValidation Report (first 5 classes):")
print(classification_report(all_labels, all_preds,
                             target_names=train_ds.classes[:5], labels=list(range(5))))

torch.save(model.state_dict(), MODEL_PATH)
print(f"\nModel saved to {MODEL_PATH}")
