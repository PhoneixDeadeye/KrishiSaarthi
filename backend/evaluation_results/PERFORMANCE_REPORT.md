# KrishiSaarthi — Performance Metrics Report

_Generated: 2026-05-05 23:30:04_

---

## A. Model Performance Metrics

### A.1 CNN — MobileNetV2 (Crop Disease Detection)

| Metric | Value |
|--------|-------|
| Architecture | MobileNetV2 (modified classifier) |
| Number of Classes | 38 |
| Total Parameters | 2,272,550 |
| Trainable Parameters | 48,678 |
| Training Epochs | 2 |
| Training Time | 3047.0s |
| Best Validation Accuracy | 89.24% |
| **Test Accuracy** | **89.33%** |
| Weighted Precision | 90.85% |
| Weighted Recall | 89.33% |
| Weighted F1-Score | 89.42% |
| Macro F1-Score | 89.37% |
| Avg Inference Time | 11.13ms/image |
| Device | cpu |
| Test Samples | 7030 |

#### Per-Class Performance (Top 10 by F1)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| Corn_(maize)___healthy | 100.0% | 100.0% | 100.0% | 185 |
| Orange___Haunglongbing_(Citrus_greening) | 97.4% | 99.5% | 98.5% | 191 |
| Corn_(maize)___Common_rust_ | 97.0% | 98.0% | 97.5% | 200 |
| Strawberry___Leaf_scorch | 95.6% | 99.4% | 97.5% | 173 |
| Grape___Leaf_blight_(Isariopsis_Leaf_Spot) | 100.0% | 94.4% | 97.1% | 180 |
| Potato___Early_blight | 98.9% | 94.9% | 96.9% | 197 |
| Squash___Powdery_mildew | 98.8% | 93.4% | 96.0% | 182 |
| Cherry_(including_sour)___healthy | 98.9% | 92.5% | 95.6% | 187 |
| Grape___Esca_(Black_Measles) | 97.7% | 93.4% | 95.5% | 181 |
| Grape___Black_rot | 95.0% | 95.9% | 95.5% | 197 |

#### Bottom 5 Classes (by F1)

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| Tomato___Septoria_leaf_spot | 68.4% | 94.1% | 79.2% | 186 |
| Tomato___Spider_mites Two-spotted_spider_mite | 89.4% | 60.4% | 72.1% | 154 |
| Tomato___Late_blight | 58.6% | 91.4% | 71.4% | 187 |
| Tomato___Early_blight | 91.2% | 57.9% | 70.8% | 178 |
| Tomato___Target_Spot | 66.7% | 73.8% | 70.1% | 195 |

#### Training Curve

| Epoch | Train Acc | Val Acc | Train Loss | Val Loss |
|-------|-----------|---------|------------|----------|
| 1 | 73.18% | 86.85% | 0.9658 | 0.4193 |
| 2 | 79.31% | 89.24% | 0.6746 | 0.3336 |

### A.2 LSTM — Risk Prediction Model

| Metric | Value |
|--------|-------|
| Architecture | LSTM(input=4, hidden=64, layers=2, dropout=0.1) -> Linear(1) -> Sigmoid |
| Input Features | vegetation_index, rainfall_mm, temperature_C, soil_moisture |
| Total Parameters | 51,265 |
| Accuracy | 98.0% |
| Precision | 98.65% |
| Recall | 97.72% |
| F1 Score | 98.18% |
| AUC-ROC | 0.9987 |
| Avg Inference | 1.107ms |
| P95 Inference | 2.409ms |

**Risk Level Distribution:** Low: 1210, Medium: 34, High: 1460

**Output Distribution:** mean=0.5465, std=0.485, min=0.0, max=1.0

#### Training Data Source

| Attribute | Details |
|-----------|---------|
| Provider | Open-Meteo ERA5 Archive (ECMWF reanalysis) |
| Temperature | ERA5 reanalysis 2m temperature |
| Precipitation | ERA5 reanalysis precipitation |
| Soil Moisture | ERA5-Land 0-7cm soil moisture |
| Vegetation | Water balance vegetation index (FAO-56 method) |
| Locations | 25 Indian agricultural districts |
| Period | 2023-01-01 to 2024-12-31 |
| Total Observations | 18,275 daily records |
| Real Data | Yes |

#### Training Details

| Attribute | Value |
|-----------|-------|
| Epochs | 30 |
| Training Time | 177.4s |
| Train/Val/Test Split | 12617 / 2704 / 2704 |
| Best Val Accuracy | 97.97% |
| High Risk % | 54.6% |

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