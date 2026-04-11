# KrishiSaarthi — Performance Metrics Report

_Generated: 2026-04-03 11:47:15_

---

## A. Model Performance Metrics

### A.1 CNN — MobileNetV2 (Crop Disease Detection)

_CNN metrics not available. Run `python scripts/train_cnn_multiclass.py` first._


### A.2 LSTM — Risk Prediction Model

| Metric | Value |
|--------|-------|
| Architecture | LSTM(input=4, hidden=64, layers=2, dropout=0.1) -> Linear(1) -> Sigmoid |
| Input Features | NDVI, rainfall_mm, temperature_C, soil_moisture |
| Total Parameters | 51,265 |
| Accuracy | 33.0% |
| Precision | 0.0% |
| Recall | 0.0% |
| F1 Score | 0.0% |
| AUC-ROC | 0.1858 |
| Avg Inference | 0.839ms |
| P95 Inference | 1.036ms |

**Risk Level Distribution:** Low: 200, Medium: 0, High: 0

**Output Distribution:** mean=0.0013, std=0.0001, min=0.0012, max=0.0018

#### Sample API Predictions

| Scenario | Risk Level | Probability | Latency |
|----------|------------|-------------|---------|
| Healthy field (high NDVI, good moisture) | Low | 0.0092 | 6.27ms |
| Stressed field (low NDVI, dry) | Low | 0.0023 | 0.94ms |
| Moderate conditions | Low | 0.0061 | 0.77ms |

---
## B. System Performance / API Benchmarks

_API benchmarks not available. Run `python scripts/benchmark_api.py` first._


---
## C. Health Score Output Validation

**Formula:** `health_score = w1 * p_cnn_healthy + w2 * ndvi_norm + w3 * (1 - risk_prob)`

**Default Weights:** CNN = 0.40, NDVI = 0.35, Risk (inverted) = 0.25

| Input Type | CNN Available | Health Score | Rating | Source |
|------------|:------------:|:-----------:|--------|--------|
| Crop image + NDVI + LSTM | Yes | 0.80 | Good | CNN + NDVI + LSTM blend |
| NDVI + LSTM only | No | 0.64 | Good | NDVI estimate (no image) |
| NDVI only (no LSTM, no image) | No | 0.56 | Fair | NDVI-only fallback |
| Image + NDVI (no LSTM) | Yes | 0.70 | Good | CNN + NDVI (no risk data) |
| All data - stressed field | Yes | 0.30 | Poor | CNN + NDVI + LSTM blend |

### Detailed Score Tests

| Scenario | CNN Prob | NDVI | Risk | Score | Rating |
|----------|---------|------|------|-------|--------|
| Healthy crop, low risk | 0.92 | 0.75 | 0.15 | 0.8430 | Excellent |
| Good crop, medium risk | 0.85 | 0.68 | 0.35 | 0.7405 | Good |
| Stressed crop, high risk | 0.45 | 0.42 | 0.72 | 0.3970 | Poor |
| Severely stressed, very high risk | 0.2 | 0.25 | 0.88 | 0.1975 | Critical |
| Neutral/uncertain all inputs | 0.5 | 0.6 | 0.5 | 0.5350 | Fair |
| Optimal conditions | 0.95 | 0.85 | 0.05 | 0.9150 | Excellent |
| Critical conditions | 0.1 | 0.15 | 0.95 | 0.1050 | Critical |

---
## D. AWD / Carbon Credit Calculation Results

### Formulas

- **water_saved_cubic_m**: `water_saved_mm * area_hectare * 10`
- **methane_baseline_kg**: `ch4_baseline_kg_per_ha_per_day (1.3) * area_ha * crop_days`
- **methane_reduction_kg**: `methane_baseline * awd_eff * awd_reduction_factor (0.35)`
- **co2e_reduction_ton**: `methane_reduction_kg * ch4_to_co2e (27.2) / 1000`
- **carbon_credits**: `co2e_reduction_ton (1 credit = 1 tonne CO2e)`
- **value_inr**: `carbon_credits * 1245 INR (= 15 USD * 83 INR/USD)`
- **simplified**: `carbon_credits * 15 * 83 = INR value`

### Sample Field Results

| Field | Area (ha) | Water Saved (m³) | CH₄ Reduced (kg) | CO₂e (t) | Credits | INR Value |
|-------|-----------|------------------|-------------------|----------|---------|-----------|
| Small rice paddy (Telangana) | 1.5 | 6,300 | 81.9 | 2.228 | 2.228 | ₹2,773 |
| Large rice field (Punjab) | 5.0 | 21,000 | 318.5 | 8.663 | 8.663 | ₹10,786 |
| Non-AWD field (continuously flooded) | 2.0 | 0 | 0.0 | 0.000 | 0.000 | ₹0 |

### AWD Detection Tests

| Pattern | AWD Detected | Cycles | Dry Ratio | Water Savings |
|---------|:------------:|:------:|:---------:|:-------------:|
| Strong AWD (3 cycles) | ✅ | 3 | 0.417 | 20.4% |
| Weak AWD (1 cycle) | ✅ | 1 | 0.167 | 14.2% |
| No AWD (always wet) | ❌ | 0 | 0.000 | 0.0% |
| No AWD (always dry) | ❌ | 0 | 1.000 | 0.0% |

---
## E. Yield Prediction Accuracy

**Method:** rule_based_ndvi

**Is ML Prediction:** False

> Yield is estimated by applying ICAR base yields scaled by NDVI, NOT by a trained ML model.

**Formula:** `yield = base_yield * (ndvi / 0.7)^ndvi_factor * trend_factor`

### Predicted Yield at NDVI = 0.70 (All Crops)

| Crop | Base Yield (kg/ha) | Predicted (kg/ha) | Regional Avg | vs Regional |
|------|-------------------|-------------------|--------------|-------------|
| Rice | 4,500 | 4,500 | 3,800 | +18% |
| Wheat | 3,500 | 3,500 | 3,100 | +13% |
| Cotton | 1,800 | 1,800 | 1,500 | +20% |
| Sugarcane | 70,000 | 70,000 | 65,000 | +8% |
| Maize | 5,000 | 5,000 | 4,200 | +19% |
| Soybean | 2,000 | 2,000 | 2,500 | -20% |
| Groundnut | 1,500 | 1,500 | 2,500 | -40% |
| Potato | 25,000 | 25,000 | 2,500 | +900% |
| Onion | 20,000 | 20,000 | 2,500 | +700% |
| Tomato | 30,000 | 30,000 | 2,500 | +1100% |

### NDVI Source Effect on Yield

| NDVI Source | NDVI | Trend | Predicted Yield | Confidence |
|------------|------|-------|-----------------|------------|
| earth_engine | 0.72 | increasing | 4,887 kg/ha | 78% |
| estimated | 0.63 | stable | 3,966 kg/ha | 75% |
| earth_engine | 0.48 | decreasing | 2,718 kg/ha | 69% |
| estimated | 0.58 | stable | 3,591 kg/ha | 73% |

### Trend Impact on Rice Yield (NDVI = 0.65)

| Trend | Predicted Yield | Factor | Impact |
|-------|-----------------|--------|--------|
| increasing | 4,323 kg/ha | 1.05 | +5% |
| stable | 4,117 kg/ha | 1.0 | +0% |
| decreasing | 3,911 kg/ha | 0.95 | -5% |

---
## F. Satellite / Earth Engine Integration

| Feature | Details |
|---------|---------|
| Data Source | Copernicus Sentinel-2 SR Harmonized |
| NDVI Formula | (B8 - B4) / (B8 + B4) |
| NDWI Formula | (B3 - B8) / (B3 + B8) |
| Rainfall Source | CHIRPS Daily |
| Temperature Source | MODIS MOD11A2 LST |
| Soil Moisture Source | ERA5-Land Daily |
| Default Date Range | Last 90 days |
| Circuit Breaker | 3 failures → OPEN, 60s recovery |
| Fallback Mechanism | Deterministic hash-based NDVI estimation |


---
## G. Finance Module Outputs

The finance module provides comprehensive farm financial management:

| Feature | Endpoint | Description |
|---------|----------|-------------|
| Cost Tracking | `/api/v1/finance/costs` | Categorized expense entries (seeds, fertilizer, labor, etc.) |
| Revenue Tracking | `/api/v1/finance/revenue` | Crop sale records with quantity, price, and buyer |
| P&L Dashboard | `/api/v1/finance/pnl` | Profit/loss summary per field and season |
| Cost Summary | `/api/v1/finance/costs/summary` | Aggregated costs by category |
| Season Management | `/api/v1/finance/seasons` | Kharif/Rabi/Zaid season tracking |
| Market Prices | `/api/v1/finance/market-prices` | Current mandi prices |
| Price Forecast | `/api/v1/finance/price-forecast` | Price trend predictions |
| Government Schemes | `/api/v1/finance/schemes` | PM-KISAN, PMFBY, and more |
| Insurance Claims | `/api/v1/finance/insurance` | PMFBY crop insurance claim tracking |
| Transactions | `/api/v1/finance/transactions` | Unified financial ledger |

---
_Report generated by KrishiSaarthi Performance Evaluation Suite_