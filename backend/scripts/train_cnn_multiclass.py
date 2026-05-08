"""
38-Class MobileNetV2 Training on PlantVillage
==============================================
Downloads PlantVillage dataset, trains MobileNetV2 with frozen backbone,
evaluates with full metrics: accuracy, precision, recall, F1, confusion matrix.

Usage:
    python scripts/train_cnn_multiclass.py
    python scripts/train_cnn_multiclass.py --dataset-path /path/to/plantvillage
    python scripts/train_cnn_multiclass.py --epochs 15 --batch-size 64
"""

import os
import sys
import time
import json
import shutil
import logging
import argparse
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import models, transforms, datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "ml_models"
RESULTS_DIR = BACKEND_DIR / "evaluation_results"
DATASET_DIR = BACKEND_DIR / "datasets" / "plantvillage"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# PlantVillage 38 class names (sorted alphabetically as ImageFolder loads them)
PLANTVILLAGE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]

HEALTHY_CLASSES = {i for i, name in enumerate(PLANTVILLAGE_CLASSES) if "healthy" in name.lower()}


def download_dataset(target_dir: Path) -> Path:
    """Download PlantVillage dataset. Returns path to image root folder."""
    if target_dir.exists() and any(target_dir.iterdir()):
        # Check if it already has the right structure
        subdirs = [d for d in target_dir.iterdir() if d.is_dir()]
        if len(subdirs) >= 30:
            logger.info("Dataset already exists at %s (%d classes)", target_dir, len(subdirs))
            return target_dir
        # Check for nested structure (e.g., from Kaggle download)
        for sub in subdirs:
            nested = [d for d in sub.iterdir() if d.is_dir()]
            if len(nested) >= 30:
                logger.info("Found dataset in nested dir: %s", sub)
                return sub

    logger.info("Downloading PlantVillage dataset...")

    # Method 1: Try kagglehub
    try:
        import kagglehub
        path = kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset")
        logger.info("Downloaded via kagglehub to: %s", path)
        # Find the actual image directory
        root = Path(path)
        for candidate in [
            root / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train",
            root / "train",
            root / "New Plant Diseases Dataset(Augmented)" / "train",
        ]:
            if candidate.exists():
                return candidate
        # Search for directory with 38 subdirs
        for dirpath, dirnames, _ in os.walk(root):
            if len(dirnames) >= 30:
                return Path(dirpath)
        return root
    except Exception as e:
        logger.warning("kagglehub download failed: %s", e)

    # Method 2: Try opendatasets
    try:
        import opendatasets as od
        od.download("https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset",
                     data_dir=str(target_dir.parent))
        dl_dir = target_dir.parent / "new-plant-diseases-dataset"
        if dl_dir.exists():
            for candidate in [
                dl_dir / "New Plant Diseases Dataset(Augmented)" / "New Plant Diseases Dataset(Augmented)" / "train",
                dl_dir / "train",
            ]:
                if candidate.exists():
                    return candidate
    except Exception as e:
        logger.warning("opendatasets download failed: %s", e)

    # Method 3: Direct Kaggle CLI
    try:
        import subprocess
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", "vipoooool/new-plant-diseases-dataset",
             "--unzip", "-p", str(target_dir.parent)],
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            dl_dir = target_dir.parent
            for candidate_name in ["New Plant Diseases Dataset(Augmented)", "new-plant-diseases-dataset"]:
                candidate = dl_dir / candidate_name
                if candidate.exists():
                    for sub in [candidate / "train", candidate / "New Plant Diseases Dataset(Augmented)" / "train"]:
                        if sub.exists():
                            return sub
    except Exception as e:
        logger.warning("Kaggle CLI download failed: %s", e)

    logger.error(
        "Could not download PlantVillage automatically.\n"
        "Please download manually from:\n"
        "  https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset\n"
        "Extract and pass --dataset-path pointing to the 'train' folder containing 38 class subdirectories."
    )
    sys.exit(1)


def build_model(num_classes: int = 38, freeze_backbone: bool = True) -> nn.Module:
    """Build MobileNetV2 with custom classifier head for multi-class."""
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(model.last_channel, num_classes),
    )

    return model.to(DEVICE)


def get_transforms():
    """Get train and val/test transforms."""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    return train_transform, val_transform


def train_model(model, train_loader, val_loader, num_epochs, lr=0.001,
                unfreeze_at=7, lr_backbone=1e-4):
    """
    Train the model with backbone unfreeze strategy.

    Phase 1 (epochs 1..unfreeze_at): Only classifier head trains (fast convergence).
    Phase 2 (epoch unfreeze_at+1..end): Entire network fine-tunes at lower LR.
    """
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    history = {"train_loss": [], "train_acc": [], "val_loss": [], "val_acc": [], "lr": []}
    best_val_acc = 0.0

    for epoch in range(1, num_epochs + 1):
        epoch_start = time.time()

        # Phase 2: Unfreeze backbone after N epochs
        if epoch == unfreeze_at + 1 and unfreeze_at > 0:
            logger.info("Epoch %d: Unfreezing backbone — LR -> %s", epoch, lr_backbone)
            for param in model.features.parameters():
                param.requires_grad = True
            optimizer = optim.Adam(model.parameters(), lr=lr_backbone)
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

        # Training phase
        model.train()
        running_loss, correct, total = 0.0, 0, 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            if (batch_idx + 1) % 100 == 0:
                logger.info(
                    "  [%d/%d] Batch %d/%d Loss: %.4f Acc: %.2f%%",
                    epoch, num_epochs, batch_idx + 1, len(train_loader),
                    loss.item(), 100.0 * correct / total
                )

        train_loss = running_loss / total
        train_acc = 100.0 * correct / total
        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)

        # Validation phase
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0

        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(DEVICE), labels.to(DEVICE)
                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        val_loss /= val_total
        val_acc = 100.0 * val_correct / val_total
        history["val_loss"].append(val_loss)
        history["val_acc"].append(val_acc)

        current_lr = optimizer.param_groups[0]["lr"]
        history["lr"].append(current_lr)

        elapsed = time.time() - epoch_start
        tag = " *BEST*" if val_acc > best_val_acc else ""
        logger.info(
            "Epoch %d/%d [%.0fs] Train: %.4f/%.2f%% | Val: %.4f/%.2f%% LR=%.6f%s",
            epoch, num_epochs, elapsed, train_loss, train_acc, val_loss, val_acc,
            current_lr, tag
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                "state_dict": model.state_dict(),
                "num_classes": 38,
                "class_names": PLANTVILLAGE_CLASSES,
                "val_acc": val_acc,
                "epoch": epoch,
            }, str(MODELS_DIR / "crop_disease_model_38class.pth"))

        scheduler.step()

    return history, best_val_acc


def evaluate_model(model, test_loader, class_names):
    """Full evaluation: accuracy, per-class precision/recall/F1, confusion matrix."""
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

    model.eval()
    all_preds = []
    all_labels = []
    inference_times = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)
            t0 = time.time()
            outputs = model(images)
            inference_times.append((time.time() - t0) / images.size(0))

            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    # Overall accuracy
    accuracy = accuracy_score(all_labels, all_preds)

    # Per-class report
    report = classification_report(
        all_labels, all_preds, target_names=class_names, output_dict=True, zero_division=0
    )

    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    # Inference stats
    avg_inference_ms = np.mean(inference_times) * 1000

    metrics = {
        "model": "MobileNetV2 (38-class)",
        "num_classes": len(class_names),
        "class_names": class_names,
        "test_accuracy": round(accuracy * 100, 2),
        "weighted_precision": round(report["weighted avg"]["precision"] * 100, 2),
        "weighted_recall": round(report["weighted avg"]["recall"] * 100, 2),
        "weighted_f1": round(report["weighted avg"]["f1-score"] * 100, 2),
        "macro_precision": round(report["macro avg"]["precision"] * 100, 2),
        "macro_recall": round(report["macro avg"]["recall"] * 100, 2),
        "macro_f1": round(report["macro avg"]["f1-score"] * 100, 2),
        "per_class": {},
        "confusion_matrix": cm.tolist(),
        "avg_inference_ms": round(avg_inference_ms, 2),
        "device": DEVICE,
        "test_samples": len(all_labels),
    }

    for cls_name in class_names:
        if cls_name in report:
            metrics["per_class"][cls_name] = {
                "precision": round(report[cls_name]["precision"] * 100, 2),
                "recall": round(report[cls_name]["recall"] * 100, 2),
                "f1": round(report[cls_name]["f1-score"] * 100, 2),
                "support": int(report[cls_name]["support"]),
            }

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Train 38-class MobileNetV2 on PlantVillage")
    parser.add_argument("--dataset-path", type=str, default=None, help="Path to dataset root with class subdirs")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--unfreeze-after", type=int, default=7, help="Unfreeze backbone after N epochs (0=never)")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("PlantVillage 38-Class CNN Training")
    logger.info("=" * 60)
    logger.info("Device: %s", DEVICE)
    logger.info("Epochs: %d, Batch Size: %d, LR: %s", args.epochs, args.batch_size, args.lr)

    # Step 1: Get dataset
    if args.dataset_path:
        dataset_root = Path(args.dataset_path)
    else:
        dataset_root = download_dataset(DATASET_DIR)

    if not dataset_root.exists():
        logger.error("Dataset path does not exist: %s", dataset_root)
        sys.exit(1)

    logger.info("Dataset root: %s", dataset_root)

    # Step 2: Load dataset with transforms
    train_transform, val_transform = get_transforms()

    # Load full dataset with train transforms first to get class info
    full_dataset = datasets.ImageFolder(str(dataset_root), transform=train_transform)
    num_classes = len(full_dataset.classes)
    logger.info("Found %d classes, %d images", num_classes, len(full_dataset))
    logger.info("Classes: %s", full_dataset.classes[:5])

    # Save class names (use actual folder names from dataset)
    class_names = full_dataset.classes

    # Split: 80% train, 10% val, 10% test
    total = len(full_dataset)
    train_size = int(0.8 * total)
    val_size = int(0.1 * total)
    test_size = total - train_size - val_size

    generator = torch.Generator().manual_seed(42)
    train_indices, val_indices, test_indices = random_split(
        range(total), [train_size, val_size, test_size], generator=generator
    )

    # Create datasets with appropriate transforms
    train_dataset = Subset(
        datasets.ImageFolder(str(dataset_root), transform=train_transform),
        train_indices.indices
    )
    val_dataset = Subset(
        datasets.ImageFolder(str(dataset_root), transform=val_transform),
        val_indices.indices
    )
    test_dataset = Subset(
        datasets.ImageFolder(str(dataset_root), transform=val_transform),
        test_indices.indices
    )

    logger.info("Split: Train=%d, Val=%d, Test=%d", len(train_dataset), len(val_dataset), len(test_dataset))

    # DataLoaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=0, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0, pin_memory=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=0, pin_memory=True)

    # Step 3: Build model
    model = build_model(num_classes=num_classes, freeze_backbone=True)
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info("Model params: %d total, %d trainable", total_params, trainable_params)

    # Step 4: Train
    logger.info("Starting training...")
    train_start = time.time()
    history, best_val_acc = train_model(
        model, train_loader, val_loader, args.epochs, args.lr,
        unfreeze_at=args.unfreeze_after, lr_backbone=args.lr * 0.1,
    )
    train_time = time.time() - train_start
    logger.info("Training completed in %.1f seconds | Best val acc: %.2f%%", train_time, best_val_acc)

    # Step 5: Load best model and evaluate
    best_ckpt = torch.load(str(MODELS_DIR / "crop_disease_model_38class.pth"), map_location=DEVICE, weights_only=True)
    model.load_state_dict(best_ckpt["state_dict"])
    logger.info("Loaded best model from epoch %d (val_acc=%.2f%%)", best_ckpt["epoch"], best_ckpt["val_acc"])

    logger.info("Evaluating on test set...")
    metrics = evaluate_model(model, test_loader, class_names)

    # Add training info
    metrics["training"] = {
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.lr,
        "training_time_seconds": round(train_time, 1),
        "total_params": total_params,
        "trainable_params": trainable_params,
        "best_epoch": best_ckpt["epoch"],
        "best_val_acc": best_ckpt["val_acc"],
        "history": history,
        "dataset_size": total,
        "train_size": train_size,
        "val_size": val_size,
        "test_size": test_size,
    }

    # Save metrics
    metrics_path = RESULTS_DIR / "cnn_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Metrics saved to %s", metrics_path)

    # Save class names mapping
    class_map_path = MODELS_DIR / "class_names_38.json"
    with open(class_map_path, "w") as f:
        json.dump({"classes": class_names, "healthy_indices": list(HEALTHY_CLASSES)}, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("CNN EVALUATION RESULTS")
    print("=" * 60)
    print(f"Model:              MobileNetV2 (38-class)")
    print(f"Device:             {DEVICE}")
    print(f"Test Accuracy:      {metrics['test_accuracy']}%")
    print(f"Weighted Precision: {metrics['weighted_precision']}%")
    print(f"Weighted Recall:    {metrics['weighted_recall']}%")
    print(f"Weighted F1:        {metrics['weighted_f1']}%")
    print(f"Avg Inference:      {metrics['avg_inference_ms']}ms/image")
    print(f"Test Samples:       {metrics['test_samples']}")
    print(f"Training Time:      {train_time:.0f}s")
    print("=" * 60)

    # Print per-class table
    print("\nPer-Class Metrics:")
    print(f"{'Class':<55} {'Prec':>6} {'Rec':>6} {'F1':>6} {'N':>5}")
    print("-" * 80)
    for cls_name, cls_metrics in metrics["per_class"].items():
        short = cls_name[:52] + "..." if len(cls_name) > 55 else cls_name
        print(f"{short:<55} {cls_metrics['precision']:>5.1f}% {cls_metrics['recall']:>5.1f}% {cls_metrics['f1']:>5.1f}% {cls_metrics['support']:>5}")


if __name__ == "__main__":
    main()
