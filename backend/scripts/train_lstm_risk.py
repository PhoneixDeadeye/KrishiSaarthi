"""
LSTM Risk Model Training with Real ERA5 Data
==============================================
Fetches real ERA5 satellite/reanalysis data from Open-Meteo API for
Indian agricultural districts. Trains LSTM on actual observations.

Data Sources (all real, no mock/synthetic):
- Temperature: ERA5 reanalysis (ECMWF)
- Precipitation: ERA5 reanalysis
- Soil Moisture: ERA5-Land (satellite-derived, 0-7cm)
- Vegetation Index: Derived from real precipitation/ET0 water balance

Locations: 25 major Indian agricultural districts
Time Period: 2023-01-01 to 2024-12-31 (2 years)
Labeling: Agronomic stress thresholds (IMD/ICAR standards)

Usage:
    python scripts/train_lstm_risk.py
    python scripts/train_lstm_risk.py --epochs 50 --seq-length 10
"""

import os
import sys
import json
import time
import logging
import argparse
import hashlib
from pathlib import Path
from datetime import datetime

import numpy as np
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
MODELS_DIR = BACKEND_DIR / "ml_models"
RESULTS_DIR = BACKEND_DIR / "evaluation_results"
CACHE_DIR = BACKEND_DIR / "datasets" / "era5_cache"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Real coordinates of major Indian agricultural districts
LOCATIONS = [
    {"name": "Ludhiana_Punjab", "lat": 30.90, "lon": 75.86},
    {"name": "Amritsar_Punjab", "lat": 31.63, "lon": 74.87},
    {"name": "Patiala_Punjab", "lat": 30.34, "lon": 76.39},
    {"name": "Karnal_Haryana", "lat": 29.69, "lon": 76.98},
    {"name": "Hisar_Haryana", "lat": 29.15, "lon": 75.72},
    {"name": "Lucknow_UP", "lat": 26.85, "lon": 80.95},
    {"name": "Prayagraj_UP", "lat": 25.43, "lon": 81.85},
    {"name": "Varanasi_UP", "lat": 25.32, "lon": 83.01},
    {"name": "Patna_Bihar", "lat": 25.61, "lon": 85.14},
    {"name": "Bhopal_MP", "lat": 23.26, "lon": 77.41},
    {"name": "Indore_MP", "lat": 22.72, "lon": 75.86},
    {"name": "Jabalpur_MP", "lat": 23.18, "lon": 79.95},
    {"name": "Nagpur_MH", "lat": 21.15, "lon": 79.09},
    {"name": "Pune_MH", "lat": 18.52, "lon": 73.86},
    {"name": "Nashik_MH", "lat": 20.00, "lon": 73.79},
    {"name": "Warangal_TS", "lat": 17.98, "lon": 79.60},
    {"name": "Guntur_AP", "lat": 16.31, "lon": 80.44},
    {"name": "Thanjavur_TN", "lat": 10.79, "lon": 79.14},
    {"name": "Coimbatore_TN", "lat": 11.01, "lon": 76.96},
    {"name": "Bardhaman_WB", "lat": 23.23, "lon": 87.87},
    {"name": "Jaipur_RJ", "lat": 26.92, "lon": 75.79},
    {"name": "Kota_RJ", "lat": 25.18, "lon": 75.86},
    {"name": "Ahmedabad_GJ", "lat": 23.02, "lon": 72.57},
    {"name": "Belgaum_KA", "lat": 15.85, "lon": 74.50},
    {"name": "Raipur_CG", "lat": 21.25, "lon": 81.63},
]

OPEN_METEO_BASE = "https://archive-api.open-meteo.com/v1/archive"


# ─────────────────────── Data Fetching ───────────────────────

def _cache_key(lat, lon, start, end):
    raw = f"{lat}_{lon}_{start}_{end}"
    return hashlib.md5(raw.encode()).hexdigest() + ".json"


def fetch_location_data(lat, lon, start_date, end_date, retries=3):
    """Fetch real ERA5 daily weather data from Open-Meteo for one location."""
    cache_file = CACHE_DIR / _cache_key(lat, lon, start_date, end_date)
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join([
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "et0_fao_evapotranspiration",
        ]),
        "timezone": "auto",
    }

    daily_data = None
    for attempt in range(retries):
        try:
            r = requests.get(OPEN_METEO_BASE, params=params, timeout=30)
            r.raise_for_status()
            daily_data = r.json()
            break
        except Exception as e:
            logger.warning("Attempt %d failed for (%.2f, %.2f): %s", attempt + 1, lat, lon, e)
            time.sleep(2 ** attempt)

    if daily_data is None or "daily" not in daily_data:
        logger.error("Failed to fetch daily data for (%.2f, %.2f)", lat, lon)
        return None

    # Fetch hourly soil moisture separately
    sm_params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "soil_moisture_0_to_7cm",
        "timezone": "auto",
    }

    hourly_sm = None
    for attempt in range(retries):
        try:
            r = requests.get(OPEN_METEO_BASE, params=sm_params, timeout=30)
            r.raise_for_status()
            sm_data = r.json()
            raw_sm = sm_data.get("hourly", {}).get("soil_moisture_0_to_7cm", [])
            if raw_sm:
                # Aggregate hourly to daily mean
                n_days = len(raw_sm) // 24
                hourly_sm = []
                for d in range(n_days):
                    chunk = raw_sm[d * 24:(d + 1) * 24]
                    valid = [v for v in chunk if v is not None]
                    hourly_sm.append(float(np.mean(valid)) if valid else None)
            break
        except Exception as e:
            logger.warning("SM attempt %d failed: %s", attempt + 1, e)
            time.sleep(2 ** attempt)

    daily = daily_data["daily"]
    n_days = len(daily["time"])

    result = {
        "dates": daily["time"],
        "temperature_mean": daily.get("temperature_2m_mean", [None] * n_days),
        "temperature_max": daily.get("temperature_2m_max", [None] * n_days),
        "temperature_min": daily.get("temperature_2m_min", [None] * n_days),
        "precipitation": daily.get("precipitation_sum", [None] * n_days),
        "et0": daily.get("et0_fao_evapotranspiration", [None] * n_days),
        "soil_moisture": hourly_sm if hourly_sm and len(hourly_sm) >= n_days else [None] * n_days,
    }

    # Cache to disk
    with open(cache_file, "w") as f:
        json.dump(result, f)

    return result


def fetch_all_locations(locations, start_date, end_date):
    """Fetch ERA5 data for all locations."""
    all_data = []
    for i, loc in enumerate(locations):
        logger.info("[%d/%d] Fetching %s (%.2f, %.2f)...",
                     i + 1, len(locations), loc["name"], loc["lat"], loc["lon"])
        data = fetch_location_data(loc["lat"], loc["lon"], start_date, end_date)
        if data:
            data["location"] = loc["name"]
            all_data.append(data)
        else:
            logger.warning("Skipping %s — no data", loc["name"])
        time.sleep(0.3)  # respect rate limits
    return all_data


# ─────────────────────── Feature Engineering ───────────────────────

def compute_vegetation_index(precip_series, et0_series, temp_series, window=14):
    """
    Compute vegetation health index from real weather data.

    Uses the crop water balance approach (FAO-56):
    - Water Supply (P) vs Water Demand (ET0)
    - Temperature suitability for crop growth
    - Smoothed over 'window' days for stability

    Returns values in [0, 1] range, analogous to NDVI.
    This is NOT mock data — it's a modeled vegetation index from real
    meteorological observations, standard practice in crop simulation
    (WOFOST, AquaCrop, DSSAT models).
    """
    n = len(precip_series)
    veg_index = np.zeros(n)

    for i in range(n):
        # Cumulative water balance over window
        start = max(0, i - window + 1)
        p_window = precip_series[start:i + 1]
        et_window = et0_series[start:i + 1]

        p_sum = np.nansum(p_window)
        et_sum = np.nansum(et_window) + 1e-5  # avoid division by zero

        # Water satisfaction ratio (WSR) — FAO method
        wsr = min(p_sum / et_sum, 1.5)

        # Temperature suitability (bell curve, optimal 20-32°C for Indian crops)
        temp = temp_series[i] if not np.isnan(temp_series[i]) else 25.0
        if 20 <= temp <= 32:
            temp_suit = 1.0
        elif 15 <= temp < 20:
            temp_suit = (temp - 15) / 5.0
        elif 32 < temp <= 40:
            temp_suit = (40 - temp) / 8.0
        elif temp < 15:
            temp_suit = max(0, (temp - 5) / 10.0)
        else:
            temp_suit = max(0, (45 - temp) / 5.0)

        # Vegetation index = water satisfaction × temperature suitability
        veg_index[i] = np.clip(wsr * temp_suit * 0.85, 0.0, 1.0)

    return veg_index


def compute_stress_label(veg, temp, precip, soil_m):
    """
    Compute binary risk label from real daily observations.

    Uses agronomic stress thresholds based on:
    - Indian Meteorological Department (IMD) heat wave criteria
    - ICAR crop stress thresholds
    - FAO water stress definitions

    Returns: 1 = high risk, 0 = low risk
    """
    stress_score = 0.0

    # Vegetation stress (low NDVI/vegetation index = stressed)
    if veg < 0.2:
        stress_score += 0.35
    elif veg < 0.35:
        stress_score += 0.20
    elif veg < 0.5:
        stress_score += 0.10

    # Temperature stress (IMD heat wave: >40°C plains, cold: <10°C)
    if temp > 42:
        stress_score += 0.30
    elif temp > 38:
        stress_score += 0.20
    elif temp > 35:
        stress_score += 0.10
    elif temp < 5:
        stress_score += 0.25
    elif temp < 10:
        stress_score += 0.15

    # Precipitation stress (drought)
    if precip < 0.5:
        stress_score += 0.20
    elif precip < 1.5:
        stress_score += 0.10

    # Soil moisture stress (wilting point ~0.10 for most Indian soils)
    if soil_m < 0.10:
        stress_score += 0.25
    elif soil_m < 0.15:
        stress_score += 0.15
    elif soil_m < 0.20:
        stress_score += 0.05

    return 1 if stress_score >= 0.45 else 0


def process_location_data(data):
    """Convert raw API data into features and labels for one location."""
    n = len(data["dates"])

    # Clean arrays — replace None with NaN
    temp = np.array([v if v is not None else np.nan for v in data["temperature_mean"]], dtype=np.float32)
    temp_max = np.array([v if v is not None else np.nan for v in data["temperature_max"]], dtype=np.float32)
    precip = np.array([v if v is not None else np.nan for v in data["precipitation"]], dtype=np.float32)
    et0 = np.array([v if v is not None else np.nan for v in data["et0"]], dtype=np.float32)
    sm = np.array([v if v is not None else np.nan for v in data["soil_moisture"][:n]], dtype=np.float32)

    # Forward-fill NaN values
    for arr in [temp, temp_max, precip, et0, sm]:
        mask = np.isnan(arr)
        if mask.all():
            arr[:] = 0.0
            continue
        idx = np.where(~mask, np.arange(len(arr)), 0)
        np.maximum.accumulate(idx, out=idx)
        arr[mask] = arr[idx[mask]]

    # Compute vegetation index from real weather data
    veg = compute_vegetation_index(precip, et0, temp)

    # Use temp_max for stress labeling (heat stress uses max temp)
    labels = np.array([
        compute_stress_label(veg[i], temp_max[i], precip[i], sm[i])
        for i in range(n)
    ], dtype=np.int64)

    # Feature matrix: [vegetation_index, rainfall_mm, temperature_C, soil_moisture]
    features = np.column_stack([veg, precip, temp, sm]).astype(np.float32)

    return features, labels


# ─────────────────────── Dataset Creation ───────────────────────

def create_sequences(features, labels, seq_length=10):
    """Create sliding window sequences for LSTM training."""
    X, y = [], []
    n = len(features)
    for i in range(n - seq_length):
        X.append(features[i:i + seq_length])
        # Label: risk at the END of the sequence
        y.append(labels[i + seq_length - 1])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64)


def build_dataset(all_location_data, seq_length=10):
    """Build full dataset from all locations."""
    all_X, all_y = [], []
    location_info = []

    for data in all_location_data:
        features, labels = process_location_data(data)
        X, y = create_sequences(features, labels, seq_length)
        if len(X) > 0:
            all_X.append(X)
            all_y.append(y)
            location_info.append({
                "name": data["location"],
                "sequences": len(X),
                "risk_ratio": float(np.mean(y)),
            })
            logger.info("  %s: %d sequences, %.1f%% high-risk",
                         data["location"], len(X), 100 * np.mean(y))

    X = np.concatenate(all_X, axis=0)
    y = np.concatenate(all_y, axis=0)

    return X, y, location_info


# ─────────────────────── Training ───────────────────────

def train_model(X_train, y_train, X_val, y_val, epochs=30, lr=0.001, batch_size=64):
    """Train LSTM model on real data."""
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader

    sys.path.insert(0, str(BACKEND_DIR))
    from ml_engine.lstm import RiskLSTM

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Training on device: %s", device)

    model = RiskLSTM(input_size=4, hidden_size=64, num_layers=2, dropout=0.1).to(device)

    # Class weights for imbalanced data
    pos_count = y_train.sum()
    neg_count = len(y_train) - pos_count
    pos_weight = torch.tensor([neg_count / (pos_count + 1e-5)], dtype=torch.float32).to(device)
    
    def criterion(output, target):
        loss = nn.BCELoss(reduction='none')(output, target)
        weight = torch.where(target == 1.0, pos_weight, torch.tensor(1.0).to(device))
        return (loss * weight).mean()

    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    train_ds = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32),
    )
    val_ds = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.float32),
    )
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_acc = 0.0
    best_state = None

    for epoch in range(epochs):
        # Train
        model.train()
        train_loss, train_correct, train_total = 0.0, 0, 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            output = model(X_batch).squeeze(-1)
            loss = criterion(output, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            train_loss += loss.item() * X_batch.size(0)
            preds = (output > 0.5).long()
            train_correct += (preds == y_batch.long()).sum().item()
            train_total += X_batch.size(0)

        train_loss /= train_total
        train_acc = 100.0 * train_correct / train_total

        # Validate
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                output = model(X_batch).squeeze(-1)
                loss = criterion(output, y_batch)
                val_loss += loss.item() * X_batch.size(0)
                preds = (output > 0.5).long()
                val_correct += (preds == y_batch.long()).sum().item()
                val_total += X_batch.size(0)

        val_loss /= val_total
        val_acc = 100.0 * val_correct / val_total
        scheduler.step(val_loss)

        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["train_acc"].append(round(train_acc, 2))
        history["val_acc"].append(round(val_acc, 2))

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            logger.info("Epoch %d/%d — Train Loss: %.4f Acc: %.1f%% | Val Loss: %.4f Acc: %.1f%% *BEST*",
                         epoch + 1, epochs, train_loss, train_acc, val_loss, val_acc)
        elif (epoch + 1) % 5 == 0:
            logger.info("Epoch %d/%d — Train Loss: %.4f Acc: %.1f%% | Val Loss: %.4f Acc: %.1f%%",
                         epoch + 1, epochs, train_loss, train_acc, val_loss, val_acc)

    # Load best model
    if best_state:
        model.load_state_dict(best_state)

    return model, history, best_val_acc


# ─────────────────────── Main ───────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train LSTM risk model on real ERA5 data")
    parser.add_argument("--start-date", default="2023-01-01")
    parser.add_argument("--end-date", default="2024-12-31")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--seq-length", type=int, default=10)
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("LSTM Risk Model Training — Real ERA5 Data")
    logger.info("=" * 60)
    logger.info("Period: %s to %s", args.start_date, args.end_date)
    logger.info("Locations: %d Indian agricultural districts", len(LOCATIONS))

    # Step 1: Fetch real data
    logger.info("\n--- Step 1: Fetching real ERA5 data from Open-Meteo ---")
    all_data = fetch_all_locations(LOCATIONS, args.start_date, args.end_date)
    logger.info("Fetched data for %d locations", len(all_data))

    if len(all_data) < 5:
        logger.error("Too few locations with data (%d). Check network.", len(all_data))
        sys.exit(1)

    # Step 2: Build dataset
    logger.info("\n--- Step 2: Building dataset from real observations ---")
    X, y, loc_info = build_dataset(all_data, args.seq_length)
    logger.info("Total sequences: %d | Features per step: %d", len(X), X.shape[2])
    logger.info("Class distribution: %.1f%% high-risk, %.1f%% low-risk",
                 100 * np.mean(y), 100 * (1 - np.mean(y)))

    # Step 3: Normalize with StandardScaler
    logger.info("\n--- Step 3: Normalizing features ---")
    from sklearn.preprocessing import StandardScaler
    import joblib

    # Reshape for scaler: (n_samples * seq_length, n_features)
    n_samples, seq_len, n_features = X.shape
    X_flat = X.reshape(-1, n_features)
    scaler = StandardScaler()
    X_flat_scaled = scaler.fit_transform(X_flat)
    X_scaled = X_flat_scaled.reshape(n_samples, seq_len, n_features)

    # Step 4: Split — 70% train, 15% val, 15% test
    logger.info("\n--- Step 4: Splitting dataset ---")
    np.random.seed(42)
    indices = np.random.permutation(len(X_scaled))
    train_end = int(0.70 * len(indices))
    val_end = int(0.85 * len(indices))

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    X_train, y_train = X_scaled[train_idx], y[train_idx]
    X_val, y_val = X_scaled[val_idx], y[val_idx]
    X_test, y_test = X_scaled[test_idx], y[test_idx]

    logger.info("Train: %d | Val: %d | Test: %d", len(X_train), len(X_val), len(X_test))

    # Save test set for independent evaluation
    test_data_path = RESULTS_DIR / "lstm_test_data.npz"
    np.savez(test_data_path, X_test=X_test, y_test=y_test)
    logger.info("Test data saved to %s", test_data_path)

    # Step 5: Train
    logger.info("\n--- Step 5: Training LSTM ---")
    train_start = time.time()
    model, history, best_val_acc = train_model(
        X_train, y_train, X_val, y_val,
        epochs=args.epochs, lr=args.lr, batch_size=args.batch_size,
    )
    train_time = time.time() - train_start
    logger.info("Training completed in %.1f seconds", train_time)

    # Step 6: Save model and scaler
    logger.info("\n--- Step 6: Saving model and scaler ---")
    import torch
    model_path = MODELS_DIR / "risk_lstm_final.pth"
    torch.save({
        "state_dict": model.state_dict(),
        "input_size": 4,
        "hidden_size": 64,
        "num_layers": 2,
        "dropout": 0.1,
    }, str(model_path))
    logger.info("Model saved to %s", model_path)

    scaler_path = MODELS_DIR / "risk_scaler.save"
    joblib.dump(scaler, str(scaler_path))
    logger.info("Scaler saved to %s", scaler_path)

    # Step 7: Evaluate on test set
    logger.info("\n--- Step 7: Evaluating on test set ---")
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.eval()
    all_probs = []
    with torch.no_grad():
        for i in range(0, len(X_test), args.batch_size):
            batch = torch.tensor(X_test[i:i + args.batch_size]).to(device)
            probs = model(batch).squeeze(-1).cpu().numpy()
            all_probs.extend(probs)

    all_probs = np.array(all_probs)
    all_preds = (all_probs > 0.5).astype(int)

    accuracy = accuracy_score(y_test, all_preds)
    precision = precision_score(y_test, all_preds, zero_division=0)
    recall = recall_score(y_test, all_preds, zero_division=0)
    f1 = f1_score(y_test, all_preds, zero_division=0)
    try:
        auc = roc_auc_score(y_test, all_probs)
    except ValueError:
        auc = None
    cm = confusion_matrix(y_test, all_preds)

    # Inference benchmark
    import torch
    times = []
    for _ in range(3):
        for i in range(min(50, len(X_test))):
            t0 = time.perf_counter()
            with torch.no_grad():
                _ = model(torch.tensor(X_test[i:i + 1]).to(device))
            times.append(time.perf_counter() - t0)

    total_params = sum(p.numel() for p in model.parameters())

    metrics = {
        "model_info": {
            "architecture": "LSTM(input=4, hidden=64, layers=2, dropout=0.1) -> Linear(1) -> Sigmoid",
            "input_features": ["vegetation_index", "rainfall_mm", "temperature_C", "soil_moisture"],
            "output": "Risk probability [0,1]",
            "total_params": total_params,
            "trainable_params": total_params,
            "hidden_size": 64,
            "num_layers": 2,
            "dropout": 0.1,
            "scaler_type": "StandardScaler",
        },
        "data_source": {
            "provider": "Open-Meteo ERA5 Archive (ECMWF reanalysis)",
            "temperature": "ERA5 reanalysis 2m temperature",
            "precipitation": "ERA5 reanalysis precipitation",
            "soil_moisture": "ERA5-Land 0-7cm soil moisture",
            "vegetation": "Water balance vegetation index (FAO-56 method)",
            "locations": len(all_data),
            "location_names": [d["location"] for d in all_data],
            "period": f"{args.start_date} to {args.end_date}",
            "total_daily_observations": sum(len(d["dates"]) for d in all_data),
            "is_real_data": True,
            "is_mock_data": False,
        },
        "training": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "seq_length": args.seq_length,
            "training_time_seconds": round(train_time, 1),
            "best_val_acc": round(best_val_acc, 2),
            "train_samples": len(X_train),
            "val_samples": len(X_val),
            "test_samples": len(X_test),
            "total_samples": len(X),
            "class_distribution": {
                "high_risk_pct": round(100 * np.mean(y), 1),
                "low_risk_pct": round(100 * (1 - np.mean(y)), 1),
            },
            "history": history,
        },
        "prediction_metrics": {
            "accuracy": round(accuracy * 100, 2),
            "precision": round(precision * 100, 2),
            "recall": round(recall * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "auc_roc": round(auc, 4) if auc else None,
            "confusion_matrix": cm.tolist(),
            "probability_distribution": {
                "mean": round(float(np.mean(all_probs)), 4),
                "std": round(float(np.std(all_probs)), 4),
                "min": round(float(np.min(all_probs)), 4),
                "max": round(float(np.max(all_probs)), 4),
                "median": round(float(np.median(all_probs)), 4),
            },
            "risk_level_counts": {
                "low": int(np.sum(all_probs < 0.4)),
                "medium": int(np.sum((all_probs >= 0.4) & (all_probs <= 0.7))),
                "high": int(np.sum(all_probs > 0.7)),
            },
            "total_samples": len(y_test),
        },
        "inference_latency": {
            "avg_ms": round(np.mean(times) * 1000, 3),
            "min_ms": round(np.min(times) * 1000, 3),
            "max_ms": round(np.max(times) * 1000, 3),
            "p95_ms": round(np.percentile(times, 95) * 1000, 3),
            "p99_ms": round(np.percentile(times, 99) * 1000, 3),
            "total_inferences": len(times),
        },
        "device": device,
        "location_details": loc_info,
    }

    metrics_path = RESULTS_DIR / "lstm_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Metrics saved to %s", metrics_path)

    # Print summary
    print("\n" + "=" * 60)
    print("LSTM TRAINING & EVALUATION RESULTS")
    print("=" * 60)
    print(f"Data Source:        ERA5 Reanalysis (Open-Meteo)")
    print(f"Locations:          {len(all_data)} Indian districts")
    print(f"Total Sequences:    {len(X):,}")
    print(f"Training Time:      {train_time:.0f}s")
    print(f"Best Val Accuracy:  {best_val_acc:.1f}%")
    print(f"Test Accuracy:      {metrics['prediction_metrics']['accuracy']}%")
    print(f"Precision:          {metrics['prediction_metrics']['precision']}%")
    print(f"Recall:             {metrics['prediction_metrics']['recall']}%")
    print(f"F1 Score:           {metrics['prediction_metrics']['f1_score']}%")
    print(f"AUC-ROC:            {metrics['prediction_metrics']['auc_roc']}")
    print(f"Avg Inference:      {metrics['inference_latency']['avg_ms']}ms")
    print("=" * 60)


if __name__ == "__main__":
    main()
