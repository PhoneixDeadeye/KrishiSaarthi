"""
LSTM Risk Model Evaluation (Real Test Data)
=============================================
Evaluates the LSTM risk model using the real held-out test set
saved during training (from ERA5 observations).

Also tests the production API format for compatibility.

Usage:
    python scripts/evaluate_lstm.py
"""

import os
import sys
import json
import time
import logging
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

import torch
from ml_engine.lstm import RiskLSTM, load_risk_model, predict_risk_from_values

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(BACKEND_DIR, "evaluation_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
TEST_DATA_PATH = os.path.join(RESULTS_DIR, "lstm_test_data.npz")


def get_model_info(model, scaler):
    """Extract model architecture info."""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return {
        "architecture": "LSTM(input=4, hidden=64, layers=2, dropout=0.1) -> Linear(1) -> Sigmoid",
        "input_features": ["NDVI", "rainfall_mm", "temperature_C", "soil_moisture"],
        "output": "Risk probability [0,1]",
        "total_params": total_params,
        "trainable_params": trainable_params,
        "hidden_size": 64,
        "num_layers": 2,
        "dropout": 0.1,
        "scaler_type": type(scaler).__name__ if scaler else "None",
    }


def load_real_test_data():
    """Load the real test data saved during training."""
    if not os.path.exists(TEST_DATA_PATH):
        logger.error(
            "Real test data not found at %s. Run train_lstm_risk.py first.",
            TEST_DATA_PATH,
        )
        return None, None

    data = np.load(TEST_DATA_PATH)
    X_test = data["X_test"]
    y_test = data["y_test"]
    logger.info("Loaded real test data: %d sequences, %d features", len(X_test), X_test.shape[2])
    return X_test, y_test


def evaluate_on_real_data(model, X_test, y_test, batch_size=64):
    """Evaluate model on real held-out test set."""
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        roc_auc_score, classification_report, confusion_matrix
    )

    model.eval()
    all_probs = []

    with torch.no_grad():
        for i in range(0, len(X_test), batch_size):
            batch = torch.tensor(X_test[i:i + batch_size], dtype=torch.float32).to(DEVICE)
            probs = model(batch).squeeze(-1).cpu().numpy()
            if probs.ndim == 0:
                probs = np.array([probs.item()])
            all_probs.extend(probs)

    all_probs = np.array(all_probs)
    all_preds = (all_probs > 0.5).astype(int)

    accuracy = accuracy_score(y_test, all_preds)
    precision = precision_score(y_test, all_preds, zero_division=0)
    recall = recall_score(y_test, all_preds, zero_division=0)
    f1 = f1_score(y_test, all_preds, zero_division=0)

    try:
        auc_roc = roc_auc_score(y_test, all_probs)
    except ValueError:
        auc_roc = None

    cm = confusion_matrix(y_test, all_preds)

    return {
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1 * 100, 2),
        "auc_roc": round(auc_roc, 4) if auc_roc else None,
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
        "data_source": "Real ERA5 held-out test set",
    }


def benchmark_inference(model, X_test, n_runs=3):
    """Benchmark inference latency on real data."""
    subset = X_test[:50]
    times = []

    for _ in range(n_runs):
        for i in range(len(subset)):
            t = torch.tensor(subset[i:i + 1], dtype=torch.float32).to(DEVICE)
            t0 = time.perf_counter()
            with torch.no_grad():
                _ = model(t)
            times.append(time.perf_counter() - t0)

    return {
        "avg_ms": round(np.mean(times) * 1000, 3),
        "min_ms": round(np.min(times) * 1000, 3),
        "max_ms": round(np.max(times) * 1000, 3),
        "p95_ms": round(np.percentile(times, 95) * 1000, 3),
        "p99_ms": round(np.percentile(times, 99) * 1000, 3),
        "total_inferences": len(times),
    }


def test_api_format():
    """Test the predict_risk_from_values API format used by views."""
    test_cases = [
        {
            "name": "Healthy field (high NDVI, good moisture)",
            "input": {
                "ndvi_time_series": [{"NDVI": 0.7}, {"NDVI": 0.72}, {"NDVI": 0.68}, {"NDVI": 0.71}],
                "rainfall_mm": 8.5,
                "temperature_K": 300,
                "soil_moisture": 0.35,
            },
        },
        {
            "name": "Stressed field (low NDVI, dry)",
            "input": {
                "ndvi_time_series": [{"NDVI": 0.25}, {"NDVI": 0.22}, {"NDVI": 0.2}, {"NDVI": 0.18}],
                "rainfall_mm": 0.5,
                "temperature_K": 313,
                "soil_moisture": 0.08,
            },
        },
        {
            "name": "Moderate conditions",
            "input": {
                "ndvi_time_series": [{"NDVI": 0.45}, {"NDVI": 0.48}, {"NDVI": 0.44}, {"NDVI": 0.46}],
                "rainfall_mm": 4.0,
                "temperature_K": 305,
                "soil_moisture": 0.2,
            },
        },
    ]

    results = []
    for case in test_cases:
        t0 = time.perf_counter()
        result = predict_risk_from_values(case["input"])
        elapsed = time.perf_counter() - t0
        result["test_name"] = case["name"]
        result["inference_ms"] = round(elapsed * 1000, 2)
        results.append(result)

    return results


def main():
    logger.info("=" * 60)
    logger.info("LSTM Risk Model Evaluation (Real Data)")
    logger.info("=" * 60)

    # Load model
    model, scaler = load_risk_model()
    if model is None or scaler is None:
        logger.error("LSTM model or scaler not found. Run train_lstm_risk.py first.")
        sys.exit(1)

    info = get_model_info(model, scaler)
    logger.info("Model: %s", info["architecture"])
    logger.info("Params: %d total", info["total_params"])

    # Load real test data
    X_test, y_test = load_real_test_data()
    if X_test is None:
        logger.error("Cannot evaluate without real test data.")
        sys.exit(1)

    # Evaluate on real data
    logger.info("Evaluating on real held-out test set (%d samples)...", len(X_test))
    pred_metrics = evaluate_on_real_data(model, X_test, y_test)

    # Benchmark inference
    logger.info("Benchmarking inference latency...")
    latency = benchmark_inference(model, X_test, n_runs=3)

    # Test API format
    logger.info("Testing API-compatible predictions...")
    api_results = test_api_format()

    # Compile report
    metrics = {
        "model_info": info,
        "prediction_metrics": pred_metrics,
        "inference_latency": latency,
        "api_test_results": api_results,
        "device": DEVICE,
    }

    # Save
    output_path = os.path.join(RESULTS_DIR, "lstm_metrics.json")
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("Results saved to %s", output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("LSTM EVALUATION RESULTS (Real Data)")
    print("=" * 60)
    print(f"Data Source:        Real ERA5 held-out test set")
    print(f"Test Samples:       {pred_metrics['total_samples']}")
    print(f"Architecture:       {info['architecture']}")
    print(f"Parameters:         {info['total_params']:,}")
    print(f"Accuracy:           {pred_metrics['accuracy']}%")
    print(f"Precision:          {pred_metrics['precision']}%")
    print(f"Recall:             {pred_metrics['recall']}%")
    print(f"F1 Score:           {pred_metrics['f1_score']}%")
    print(f"AUC-ROC:            {pred_metrics['auc_roc']}")
    print(f"Avg Inference:      {latency['avg_ms']}ms")
    print(f"P95 Inference:      {latency['p95_ms']}ms")
    print("=" * 60)

    print("\nRisk Distribution:")
    rc = pred_metrics["risk_level_counts"]
    print(f"  Low:    {rc['low']}")
    print(f"  Medium: {rc['medium']}")
    print(f"  High:   {rc['high']}")

    print("\nAPI Test Results:")
    for r in api_results:
        name = r.get("test_name", "?")
        risk = r.get("risk_level", "?")
        prob = r.get("risk_probability", "?")
        ms = r.get("inference_ms", "?")
        print(f"  {name}: risk={risk} (prob={prob}) [{ms}ms]")


if __name__ == "__main__":
    main()
