# 🎓 KrishiSaarthi (AgriSmart) — Viva Preparation Document

> **Project:** Intelligent Agriculture Management Platform  
> **Tech Stack:** Django 5.1 + React 18 + PyTorch + Google Earth Engine + Gemini AI  
> **Author:** Rohan Agarwal | Capstone Project 2026

---

## 1. PROJECT OVERVIEW

### 1.1 Objective
To build a **production-ready, AI-powered agricultural management platform** that leverages satellite imagery, deep learning, and real-time analytics to help farmers make data-driven decisions about crop health, pest management, finances, and sustainability.

### 1.2 Problem Statement
Indian farmers face critical challenges:
- **Manual crop monitoring** is time-consuming and error-prone
- **Pest/disease detection** requires expert knowledge unavailable in rural areas
- **Financial tracking** is scattered across multiple systems
- **Weather impacts** are unpredictable without data-driven forecasting
- **Carbon credit opportunities** from sustainable practices are missed

### 1.3 Motivation
- Agriculture employs ~42% of India's workforce but lacks technological tools
- Crop losses due to pests/diseases cost ₹50,000+ crore annually
- Small farmers need affordable, accessible AI-powered tools
- Sustainability practices (AWD) can reduce methane emissions by 30-50%
- Bridging the gap between satellite data availability and farmer accessibility

### 1.4 Real-World Applications
- **Precision farming** for small/medium Indian farms
- **Early warning systems** for pest/disease outbreaks
- **Carbon credit marketplace** participation for rice paddies
- **Government scheme discovery** for subsidies
- **Market price forecasting** for better selling decisions

### 1.5 Edge Over Similar Projects
- **Multi-modal fusion, not a single model**: combines satellite data, crop images, time-series risk, weather, finance, and sustainability analytics.
- **Real data sources**: Google Earth Engine, OpenWeather, data.gov.in mandi data, and live field geometry instead of prefilled mock dashboards.
- **Actionable outputs**: health score, pest diagnosis, risk level, carbon credits, scheme matching, and market tips are all decision-ready.
- **Graceful fallback design**: if EE, Gemini, or another API fails, the app still returns safe defaults instead of breaking.
- **Production-minded architecture**: token auth, caching, model registry, lazy loading, and modular app boundaries.
- **Farmer-friendly UX**: polygon drawing, multilingual labels, responsive UI, and readable contrast across screens.

### 1.6 Latest Implementation Updates
- **Shared GET caching and request deduplication** were added to the frontend API client, so repeated GET calls are reused across dashboard cards and report pages.
- **Field list loading now uses the cached API client**, which reduces redundant startup requests.
- **Cache invalidation on logout** prevents stale user-specific data from persisting between sessions.
- **Weather and health hooks now use shared query keys**, so dashboard and report views reuse the same cached response.
- **Pest recommendations and yield recommendations were upgraded to dynamic AI-assisted outputs**, with deterministic fallback logic when the model is unavailable.
- **Market price tips and scheme matching were modernized** to support live or AI-generated guidance instead of static filler text.

---

## 2. TECHNICAL EXPLANATION

### 2.1 Step-by-Step Working
1. **User Registration** → Token-based authentication (DRF)
2. **Field Creation** → User draws polygon on Leaflet map → coordinates stored
3. **Satellite Analysis** → Google Earth Engine computes NDVI, EVI, SAVI, NDWI
4. **Pest Detection** → User uploads crop image → Gemini Vision validates → MobileNetV2 CNN classifies into 38 diseases
5. **Risk Prediction** → 14-day NDVI + weather time series → LSTM predicts risk
6. **Health Score** → Weighted fusion: CNN(0.30) + NDVI(0.25) + LSTM(0.20) + Weather(0.15) + Practice(0.10)
7. **Carbon Credits** → NDWI-based AWD detection → IPCC Tier-2 methane calculations
8. **Financial Tracking** → Cost/Revenue/P&L per season
9. **AI Chatbot** → Gemini 2.5 Flash with agricultural system prompt

### 2.2 Architecture (Text Description)
```
CLIENT LAYER: React 18 + TypeScript + TailwindCSS 4 + Vite
    ↓ REST API (Token Auth)
API LAYER: Django 5.1 + Django REST Framework
    ↓
THREE MODULES: Field | Finance | Planning
    ↓
ML/AI LAYER: MobileNetV2 CNN | LSTM Risk | Gemini 2.5 Flash
    ↓
EXTERNAL: Google Earth Engine | OpenWeather API | Gemini AI
```
- **Client → API**: REST calls with Token authentication
- **API → ML**: Lazy-loaded PyTorch models via `ml_engine` package
- **API → External**: Earth Engine for satellite data, Gemini for chat/vision

### 2.3 Algorithms Used

#### CNN — MobileNetV2 (38-class Plant Disease Detection)
- **Base**: MobileNetV2 pretrained on ImageNet (transfer learning)
- **Why MobileNetV2**: Lightweight (9.1MB), uses depthwise separable convolutions, ideal for deployment
- **Classifier**: `Dropout(0.2) → Linear(1280, 38)`
- **Training Strategy**: Freeze backbone for 7 epochs, then unfreeze with 10x lower LR
- **Input**: 224×224 RGB, normalized with ImageNet mean/std
- **Output**: Softmax probabilities across 38 PlantVillage classes
- **Loss**: CrossEntropyLoss
- **Optimizer**: Adam with StepLR scheduler
- **Data Augmentation**: RandomResizedCrop, HorizontalFlip, Rotation(15°), ColorJitter

#### LSTM — Risk Prediction
- **Architecture**: `LSTM(input=4, hidden=64, layers=2, dropout=0.1) → Linear(1) → Sigmoid`
- **Input Features**: [vegetation_index, rainfall_mm, temperature_C, soil_moisture]
- **Sequence Length**: 10-14 day sliding window
- **Data Source**: Real ERA5 reanalysis data from 25 Indian agricultural districts
- **Labeling**: Agronomic stress thresholds (IMD/ICAR standards)
- **Scaler**: StandardScaler (scikit-learn) for input normalization
- **Loss**: BCELoss (binary classification)

#### Health Score — Weighted Ensemble Fusion
```
HealthScore = 0.30×CNN + 0.25×NDVI + 0.20×(1-Risk) + 0.15×Weather + 0.10×Practice
```
- All components normalized to [0,1]
- LSTM risk is inverted (high risk = low health)
- Weather derived from temperature/rainfall/soil moisture optimality
- Practice derived from NDWI-based AWD detection

#### AWD Detection — State Machine on NDWI Time Series
- Tracks wet/dry state transitions using NDWI thresholds (wet>0.3, dry<0.2)
- Counts complete wet→dry→wet cycles
- Estimates water savings (15-30%) and methane reduction

#### Carbon Credit Calculation — IPCC Tier-2
- `EF_continuous = 1.30 kg CH4/ha/day`
- `EF_AWD = 0.55 kg CH4/ha/day`
- `GWP100 = 27.9 (CH4 → CO2e)`
- `Carbon Price = $15/tonne CO2e`

### 2.4 Technologies & Libraries

| Layer | Technology | Why Chosen |
|-------|-----------|------------|
| **Frontend** | React 18 + TypeScript | Type safety, component reusability, large ecosystem |
| **Styling** | TailwindCSS 4 + Shadcn UI | Utility-first, consistent design system |
| **Bundler** | Vite | Fast HMR, ES modules, 10-100x faster than Webpack |
| **Backend** | Django 5.1 + DRF | Batteries-included, ORM, auth, admin panel |
| **ML Framework** | PyTorch 2.5 | Dynamic computation graphs, research-friendly |
| **Satellite** | Google Earth Engine | Petabyte-scale geospatial analysis |
| **AI/LLM** | Google Gemini 2.5 Flash | Multimodal (vision+text), fast, cost-effective |
| **Maps** | Leaflet + React-Leaflet | Open-source, lightweight, mobile-friendly |
| **Charts** | Recharts | React-native, composable, responsive |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Zero-config dev, scalable prod |
| **Geospatial** | Shapely + PyProj | UTM projection for accurate area calculation |
| **State** | TanStack React Query | Server state caching, auto-refetching |
| **Routing** | Wouter | Lightweight alternative to React Router |
| **Auth** | DRF Token Auth | Simple, stateless, suitable for SPA |

---

## 3. KEY CONCEPTS TO REMEMBER

### Definitions
- **NDVI** (Normalized Difference Vegetation Index): `(NIR - Red) / (NIR + Red)`, range [-1,1], >0.3 = healthy vegetation
- **NDWI** (Normalized Difference Water Index): Detects water content in vegetation
- **EVI** (Enhanced Vegetation Index): Corrects atmospheric/soil effects vs NDVI
- **SAVI** (Soil Adjusted Vegetation Index): Minimizes soil brightness influence
- **AWD** (Alternate Wetting & Drying): Water-saving rice irrigation technique
- **Transfer Learning**: Using pretrained model weights (ImageNet) for new task
- **MobileNetV2**: Google's efficient CNN using depthwise separable convolutions and inverted residuals
- **LSTM**: Long Short-Term Memory — RNN variant with forget/input/output gates
- **GWP100**: Global Warming Potential over 100 years (CH4 = 27.9× CO2)
- **ERA5**: ECMWF's global atmospheric reanalysis dataset
- **REST API**: Representational State Transfer — stateless client-server architecture
- **Token Authentication**: Stateless auth where client sends token in header

### Core Concepts
- **Depthwise Separable Convolution**: Splits standard convolution into depthwise (per-channel) + pointwise (1×1), reducing computation by 8-9×
- **Inverted Residual Block**: MobileNetV2's core — expand→depthwise→project with skip connections
- **Softmax**: Converts logits to probability distribution summing to 1
- **Sigmoid**: Maps value to [0,1] for binary classification
- **StandardScaler**: `z = (x - μ) / σ` — zero mean, unit variance normalization
- **Lazy Loading**: Models loaded on first request, not at server startup
- **Singleton Pattern**: ModelRegistry uses `__new__` to ensure single instance

---

## 4. POSSIBLE VIVA QUESTIONS & ANSWERS

### 4.1 Basic Questions

**Q: What is your project about?**  
A: KrishiSaarthi is an AI-powered agricultural management platform that uses satellite imagery (Google Earth Engine), deep learning (CNN for pest detection, LSTM for risk prediction), and LLM-based chatbot (Gemini) to help farmers monitor crop health, detect diseases, predict risks, track finances, and earn carbon credits.

**Q: What dataset did you use for CNN training?**  
A: PlantVillage dataset — 54,305 images across 38 classes (14 crop species, 26 diseases + 12 healthy classes). Downloaded via Kaggle.

**Q: What is NDVI and why is it important?**  
A: NDVI = (NIR - Red)/(NIR + Red). It measures vegetation health from satellite imagery. Values >0.3 indicate healthy green vegetation. We use it as a key input for health scoring and risk prediction.

**Q: Why did you choose Django over Flask/FastAPI?**  
A: Django provides batteries-included features: ORM, admin panel, authentication, migrations, and DRF for API building. For a full-stack application with multiple modules (field, finance, planning), Django's structure is more maintainable.

**Q: How does authentication work?**  
A: Token-based authentication via DRF. User logs in → receives token → sends `Authorization: Token <token>` header with every request. All data endpoints filter by `request.user` to prevent unauthorized access.

### 4.2 Intermediate Questions

**Q: Explain the CNN architecture in detail.**  
A: We use MobileNetV2 pretrained on ImageNet. The original classifier (1000 classes) is replaced with `Dropout(0.2) → Linear(1280, 38)` for 38 PlantVillage classes. Training uses a 2-phase strategy: Phase 1 (epochs 1-7) freezes the backbone and trains only the classifier head; Phase 2 unfreezes the entire network with 10× lower learning rate for fine-tuning. Input images are resized to 224×224 and normalized with ImageNet statistics.

**Q: How does the LSTM predict risk?**  
A: The LSTM takes a 10-14 day sequence of [vegetation_index, rainfall, temperature, soil_moisture] as input. Each timestep has 4 features. The 2-layer LSTM processes the sequence, takes the output of the last timestep, passes it through `Linear(64,1) → Sigmoid` to produce a risk probability [0,1]. Values >0.7 = High Risk, 0.4-0.7 = Medium, <0.4 = Low.

**Q: What is the Health Score formula?**  
A: `HealthScore = 0.30×P(CNN_healthy) + 0.25×NDVI_norm + 0.20×(1-Risk) + 0.15×Weather + 0.10×Practice`. Each component is normalized to [0,1]. The weights were chosen to prioritize image-based diagnosis (CNN) and vegetation status (NDVI) while incorporating temporal risk, environmental conditions, and farming practices.

**Q: How do you handle the case when ML models aren't available?**  
A: All models use lazy loading with graceful fallback. If a model file is missing, the system returns `fallback: True` with neutral values (probability=0.5). The health score computation handles missing components by using default neutral values (0.5) for unavailable inputs.

**Q: How does AWD detection work?**  
A: We analyze NDWI time series using a state machine. When NDWI > 0.3, the field is "wet"; when NDWI < 0.2, it's "dry". We track transitions from dry→wet as complete cycles. If ≥1 cycle is detected, AWD is confirmed. More cycles with higher dry ratios indicate better water management.

### 4.3 Advanced Questions

**Q: Why MobileNetV2 over ResNet or VGG?**  
A: MobileNetV2 uses depthwise separable convolutions and inverted residual blocks, making it ~10× smaller (9.1MB vs 100+MB for ResNet-50) with comparable accuracy. This is critical for deployment — our model loads fast, uses minimal memory, and allows CPU inference in production.

**Q: How do you prevent overfitting in CNN training?**  
A: Multiple strategies: (1) Data augmentation (random crop, flip, rotation, color jitter), (2) Dropout(0.2) in classifier, (3) Gradient clipping (max_norm=1.0), (4) StepLR scheduler (halve LR every 5 epochs), (5) Early stopping via best-model checkpointing, (6) Backbone freezing in early epochs to prevent catastrophic forgetting.

**Q: How is the LSTM trained on real data, not synthetic?**  
A: We fetch real ERA5 reanalysis data from Open-Meteo API for 25 Indian agricultural districts (Ludhiana, Karnal, Varanasi, etc.) covering 2023-2024. Features include actual temperature, precipitation, soil moisture, and ET0. Vegetation index is computed using FAO-56 water balance method. Risk labels use IMD/ICAR agronomic stress thresholds — not arbitrary labels.

**Q: Explain the Model Registry and why it matters.**  
A: The ModelRegistry is a Singleton class that tracks all ML models with: version numbers, SHA-256 file hashes for integrity verification, file sizes, architecture metadata, and input/output specs. It ensures reproducibility (which exact model version produced a prediction) and detects corrupted model files at startup.

**Q: How do you handle security?**  
A: (1) Login rate limiting (5/min/IP), (2) User-scoped queries (all data filtered by request.user), (3) IDOR prevention (session ownership verified), (4) PII encryption at rest (Fernet for bank details), (5) Input sanitization (question length limits, coordinate validation), (6) CSRF/XSS protection, (7) HttpOnly session cookies.

**Q: How does Gemini Vision validate images before CNN prediction?**  
A: Before running CNN inference, the uploaded image is sent to Gemini Vision API to verify it's actually a plant/crop image (not a random photo). This prevents meaningless predictions on non-agricultural images and improves user experience.

### 4.4 Cross-Questions (Follow-ups)

**Q: If NDVI alone can indicate crop health, why use CNN?**  
A: NDVI shows overall vegetation vigor but cannot identify SPECIFIC diseases. A field might have normal NDVI but early-stage localized disease. CNN identifies the exact disease (e.g., "Tomato Late Blight") from close-up images, enabling targeted treatment.

**Q: Why not use a single model instead of the ensemble health score?**  
A: Different data sources capture different aspects. CNN sees leaf-level symptoms; NDVI shows field-level vigor; LSTM captures temporal trends; weather indicates environmental stress. A single model would miss cross-domain signals. The weighted fusion provides robust, multi-perspective assessment.

**Q: What if the Earth Engine API is down?**  
A: The system handles this gracefully. EE calls are wrapped in try-except blocks. If satellite data is unavailable, health score uses neutral fallback values (0.5) for NDVI and weather components. The CNN can still process uploaded images independently.

---

## 5. CODE-LEVEL QUESTIONS

### 5.1 Important Functions

**`predict_health(img_path)` in `cnn.py`**  
Opens image → converts to RGB → applies transforms (resize 224, normalize) → runs through MobileNetV2 → for multiclass: softmax → top-3 predictions, confidence level, crop/disease extraction → returns structured dict.

**`predict_risk_from_values(sequence)` in `lstm.py`**  
Accepts dict or list → parses to numpy array → handles NaN → scales with StandardScaler → converts to tensor → LSTM forward pass → sigmoid output → risk level categorization.

**`compute_health_score()` in `health_score.py`**  
Takes 5 normalized inputs → applies weights (0.30, 0.25, 0.20, 0.15, 0.10) → clips result to [0,1] → returns composite score.

**`detect_awd_from_ndwi()` in `awd.py`**  
Iterates NDWI series → tracks wet/dry states → counts cycles → calculates dry ratio → estimates water savings (10-30%) and methane reduction.

**`calculate_carbon_metrics()` in `cc.py`**  
Calls AWD detection → determines efficiency factor → computes water saved, methane reduction (IPCC), CO2 equivalent, carbon credits, and monetary value in INR.

### 5.2 Why Specific Techniques

| Technique | Why Used | Alternative |
|-----------|----------|-------------|
| Lazy loading (`get_model()`) | Avoids loading PyTorch at server start; only loads when first prediction requested | Eager loading (slower startup) |
| `torch.no_grad()` | Disables gradient computation during inference, saving memory and speed | Not using it (wastes GPU memory) |
| `model.eval()` | Disables dropout and batch norm training behavior during inference | Forgetting this causes inconsistent predictions |
| StandardScaler | Normalizes LSTM inputs to zero mean, unit variance for stable training | MinMaxScaler (sensitive to outliers) |
| ImageNet normalization | MobileNetV2 was trained with these stats; using different normalization breaks transfer learning | Random normalization (breaks pretrained weights) |
| Singleton Registry | Single source of truth for model metadata; prevents duplicate instances | Global dict (no encapsulation) |

---

## 6. ADVANTAGES & LIMITATIONS

### Strengths
- **Multi-modal AI**: Combines satellite, image, time-series, and LLM analysis
- **Real satellite data**: Google Earth Engine (not mock data)
- **38-class disease detection**: Covers 14 crop species with specific disease identification
- **Real ERA5 training data**: LSTM trained on actual meteorological observations from 25 Indian districts
- **Production-ready**: Docker, CI/CD, rate limiting, encryption, monitoring
- **Comprehensive modules**: Field + Finance + Planning + Chat
- **Multi-language support**: English, Hindi, Punjabi, Malayalam
- **Carbon credit estimation**: IPCC-standard calculations with AWD detection
- **Graceful degradation**: Works even when ML models or APIs are unavailable

### Limitations
- **Internet dependent**: Requires connectivity for Earth Engine, Gemini, weather APIs
- **PlantVillage bias**: CNN trained on lab-controlled images; may underperform on field photos
- **Limited crops**: 14 species covered; many Indian crops (rice blast, sugarcane) not included
- **No real-time processing**: Satellite data has temporal lag (5-16 days)
- **SQLite in dev**: Not suitable for concurrent multi-user production
- **No offline mode**: Full functionality requires API access
- **LSTM limited features**: Currently uses 4 features; could benefit from more (humidity, wind)

---

## 7. FUTURE SCOPE

- **Drone integration**: Real-time high-resolution field imagery
- **Edge deployment**: Run CNN on mobile devices using ONNX/TFLite
- **More crop species**: Expand beyond PlantVillage to Indian-specific datasets
- **Real-time alerts**: Push notifications for sudden NDVI drops or weather events
- **Marketplace**: Direct farmer-to-buyer crop selling platform
- **IoT sensor integration**: Soil moisture sensors, weather stations
- **Federated learning**: Train models on farmer data without centralizing it
- **Multilingual voice**: Full voice-based interaction in regional languages
- **Crop insurance automation**: Auto-generate claim reports from satellite evidence
- **Blockchain**: Tamper-proof carbon credit verification

---

## 8. PRACTICAL DEMONSTRATION QUESTIONS

**Q: Show me how pest detection works.**  
A: Navigate to Field → Upload Pest Image → Gemini validates it's a plant → CNN returns disease name, confidence, top-3 predictions. Demo with a tomato leaf image.

**Q: How accurate is the health score?**  
A: Show the breakdown panel — each component (CNN, NDVI, LSTM, Weather, Practice) with individual scores and weights. Health Score = weighted sum, rated Excellent/Good/Fair/Poor/Critical.

**Q: What happens if I upload a non-plant image?**  
A: Gemini Vision pre-validates the image. If it's not a plant, the system rejects it before wasting CNN inference.

**Q: Show the satellite analysis.**  
A: Select a field → View NDVI/EVI/SAVI time series charts → Show color-coded vegetation health → Explain trends (seasonal patterns, stress events).

**Q: How does the chatbot handle non-agricultural questions?**  
A: The system prompt instructs Gemini to "redirect politely if asked about non-agriculture topics." Demo by asking a non-agricultural question.

---

## 9. IMPORTANT FACTS & ONE-LINERS

- **MobileNetV2 model size**: ~9.1 MB (binary) / varies for 38-class
- **LSTM parameters**: input=4, hidden=64, layers=2, dropout=0.1
- **Health Score weights**: CNN=0.30, NDVI=0.25, LSTM=0.20, Weather=0.15, Practice=0.10
- **CNN input size**: 224×224×3 (RGB)
- **ImageNet normalization**: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- **NDVI formula**: (NIR - Red) / (NIR + Red)
- **AWD thresholds**: wet > 0.3 NDWI, dry < 0.2 NDWI
- **IPCC CH4 GWP100**: 27.9
- **Continuous flooding emission**: 1.30 kg CH4/ha/day
- **AWD emission**: 0.55 kg CH4/ha/day
- **Carbon price**: $15/tonne CO2e × ₹83 = ₹1,245/tonne
- **Training data**: 25 Indian districts, 2 years ERA5 reanalysis (2023-2024)
- **API endpoints**: 45 unique functional endpoints
- **Frontend components**: 79 files across 9 directories
- **PlantVillage**: 54,305 images, 38 classes, 14 crop species
- **Transfer Learning**: Reuse ImageNet features → fine-tune for new task
- **Depthwise Separable Conv**: Reduces computation by ~8-9× vs standard convolution
- **Sigmoid**: σ(x) = 1/(1+e^(-x)), maps to [0,1]
- **Softmax**: e^(xi) / Σe^(xj), maps to probability distribution

---

## 10. TROUBLESHOOTING & EDGE CASES

| Issue | Cause | Solution |
|-------|-------|----------|
| CNN returns "Unknown" | Model file missing | Check `ml_models/crop_health_model.pth` exists |
| LSTM fallback values | Scaler or model missing | Verify `risk_lstm_final.pth` and `risk_scaler.save` |
| Earth Engine auth fail | Token expired | Run `earthengine authenticate` |
| CORS errors | Frontend origin not whitelisted | Add to `CORS_ALLOWED_ORIGINS` in `.env` |
| Gemini 502 error | API key missing/invalid | Check `GEMINI_API_KEY` in backend `.env` |
| Low CNN confidence | Blurry/non-standard image | Use clear, well-lit leaf close-ups |
| Health score = 0.5 | All components unavailable | Ensure at least one data source works |
| NaN in LSTM input | Missing satellite data | `nan_to_num()` replaces NaN with 0.0 |
| Area calculation wrong | Invalid polygon | Need ≥3 coordinate points |
| Batch inference OOM | Too many images at once | Reduce batch size |

---

## 11. SUMMARY FOR LAST-MINUTE REVISION

### The Project in 30 Seconds
> KrishiSaarthi is an AI-powered farm management platform using **MobileNetV2 CNN** (38-class disease detection on PlantVillage), **LSTM** (risk prediction from ERA5 satellite data), **Google Earth Engine** (NDVI/NDWI vegetation indices), **Gemini AI** (chatbot + image validation), with a **React+Django** full-stack architecture. It provides health scoring (weighted ensemble of 5 factors), carbon credit estimation (IPCC methodology), financial tracking, and multi-language support.

### Key Numbers to Remember
- **38** disease classes, **14** crop species (PlantVillage)
- **5** health score components with weights summing to **1.0**
- **25** Indian agricultural districts for LSTM training
- **4** LSTM input features, **64** hidden units, **2** layers
- **224×224** CNN input resolution
- **45** API endpoints, **79** frontend component files

### Architecture in One Line
**React 18 (Vite) → Django REST API (Token Auth) → PyTorch ML Engine (CNN + LSTM) + Google Earth Engine + Gemini 2.5 Flash**

### Why Each Model
- **CNN**: Identify WHICH disease from leaf image (visual diagnosis)
- **LSTM**: Predict WHEN risk will occur from weather trends (temporal forecasting)
- **Health Score**: HOW healthy overall (multi-factor fusion)
- **AWD**: WHETHER sustainable irrigation is practiced (pattern detection)

### Security Checklist
✅ Token auth ✅ User-scoped queries ✅ Rate limiting ✅ Input sanitization ✅ PII encryption ✅ IDOR prevention ✅ CSRF protection

---

## 12. TEAM RESPONSIBILITY DIVISION (6 Members)

> **Rule:** Every member must know the **full project overview** (Section 1) and the **architecture** (Section 2.2). Below is the **primary ownership** — each person leads their module but must have basic knowledge of all others.

---

### 👤 Member 1 — CNN & Image-Based Pest Detection

**Primary Responsibility:** Disease detection pipeline — from image upload to prediction result.

| Area | Details |
|------|---------|
| **Modules Owned** | `ml_engine/cnn.py`, `scripts/train_cnn_multiclass.py`, `field/views/analysis.py` (pest report endpoint) |
| **Key Work** | MobileNetV2 architecture, transfer learning, 38-class PlantVillage training, data augmentation, Gemini Vision image validation |
| **Frontend** | Pest Detection upload UI, results display with confidence scores |
| **Dataset** | PlantVillage — 54,305 images, 38 classes, 14 crop species |

**Must-Know Viva Questions:**
- What is MobileNetV2? Why over ResNet/VGG?
- Explain depthwise separable convolutions and inverted residual blocks
- What is transfer learning? How did you fine-tune?
- Training strategy — freeze/unfreeze backbone, learning rate scheduling
- What is softmax? How do you get top-3 predictions?
- Data augmentation techniques used and why
- How does Gemini Vision validate images before CNN inference?
- Input preprocessing — 224×224, ImageNet normalization values
- Handling multi-class vs binary fallback

### 4.5 Suggested Answers — Member 1

**Q: What is MobileNetV2? Why over ResNet/VGG?**  
A: MobileNetV2 is a lightweight CNN designed for efficient inference. It gives strong transfer-learning performance with far fewer parameters than ResNet or VGG, so it loads faster and is easier to deploy.

**Q: Explain depthwise separable convolutions and inverted residual blocks**  
A: Depthwise separable convolution splits a standard convolution into a per-channel depthwise step and a 1x1 pointwise step, which reduces computation. Inverted residual blocks expand channels, apply depthwise convolution, then project back while keeping skip connections for efficiency.

**Q: What is transfer learning? How did you fine-tune?**  
A: Transfer learning means reusing pretrained ImageNet weights and adapting them to crop disease classes. I replaced the final classifier, trained the head first, then unfroze the backbone for fine-tuning with a lower learning rate.

**Q: Training strategy — freeze/unfreeze backbone, learning rate scheduling**  
A: I froze the backbone in the first phase so the classifier learned stable disease-specific features, then unfroze the model for fine-tuning. A scheduler reduced the learning rate as training progressed, which improved convergence.

**Q: What is softmax? How do you get top-3 predictions?**  
A: Softmax converts logits into probabilities that sum to 1. I sort the predicted probabilities and return the top three classes with confidence scores for better interpretability.

**Q: Data augmentation techniques used and why**  
A: I used crop and resize, flips, rotation, and color jitter so the model sees more variation and generalizes better to real field images, lighting changes, and leaf orientations.

**Q: How does Gemini Vision validate images before CNN inference?**  
A: Gemini Vision checks whether the uploaded image is actually a crop or leaf image before the CNN runs. That avoids meaningless predictions on screenshots, objects, or non-plant photos.

**Q: Input preprocessing — 224x224, ImageNet normalization values**  
A: Images are resized to 224x224 because that matches MobileNetV2 input expectations. I normalize with ImageNet mean and standard deviation so the pretrained backbone receives data in the same distribution it was trained on.

**Q: Handling multi-class vs binary fallback**  
A: The main disease model is multi-class for 38 PlantVillage categories. If a fallback path is used, the system returns a safe neutral output instead of producing a misleading hard error.


---

### 👤 Member 2 — LSTM & Risk Prediction

**Primary Responsibility:** Time-series risk forecasting — from data fetching to risk output.

| Area | Details |
|------|---------|
| **Modules Owned** | `ml_engine/lstm.py`, `scripts/train_lstm_risk.py`, `field/views/analysis.py` (pest predict endpoint) |
| **Key Work** | LSTM architecture, ERA5 data pipeline, feature engineering, StandardScaler, risk labeling with IMD/ICAR thresholds |
| **Data Source** | Open-Meteo ERA5 Archive — 25 Indian agricultural districts, 2023-2024 |
| **Training** | Sliding window (seq_len=10), 70/15/15 split, BCELoss, Adam + ReduceLROnPlateau |

**Must-Know Viva Questions:**
- What is LSTM? Explain forget/input/output gates
- How is it different from vanilla RNN? (Vanishing gradient problem)
- What are the 4 input features and why those?
- How did you get real training data? Explain ERA5 and Open-Meteo
- What is StandardScaler and why is it needed?
- How are risk labels generated? (Agronomic stress thresholds)
- Explain the vegetation index computation (FAO-56 water balance)
- Sequence length choice — why 10-14 days?
- What does `model(x)[:, -1, :]` mean? (Last timestep output)

### 4.6 Suggested Answers — Member 2

**Q: What is LSTM? Explain forget/input/output gates**  
A: LSTM is a recurrent neural network designed for sequence data. The forget gate decides what to remove from memory, the input gate decides what new information to store, and the output gate decides what to expose as the current hidden state.

**Q: How is it different from vanilla RNN? (Vanishing gradient problem)**  
A: Vanilla RNNs struggle to keep long-term information because gradients vanish or explode over long sequences. LSTMs solve that with gated memory cells, so they learn longer temporal dependencies more reliably.

**Q: What are the 4 input features and why those?**  
A: The model uses vegetation index, rainfall, temperature, and soil moisture because they are the most direct indicators of crop stress and environmental risk in the current pipeline.

**Q: How did you get real training data? Explain ERA5 and Open-Meteo**  
A: I used real meteorological reanalysis data from ERA5 through Open-Meteo for multiple Indian districts. That gives historical, location-based climate patterns instead of synthetic sequences.

**Q: What is StandardScaler and why is it needed?**  
A: StandardScaler normalizes each feature to zero mean and unit variance. This helps the LSTM train stably because one feature does not dominate the others just due to scale.

**Q: How are risk labels generated? (Agronomic stress thresholds)**  
A: Labels are generated from agronomic stress thresholds derived from crop-condition rules, so the model learns meaningful high-risk and low-risk patterns instead of arbitrary labels.

**Q: Explain the vegetation index computation (FAO-56 water balance)**  
A: The vegetation proxy is built from water-balance style agronomic features that reflect how moisture stress and weather influence crop condition over time.

**Q: Sequence length choice — why 10-14 days?**  
A: That window is long enough to capture short-term weather and vegetation trends but still compact enough to keep inference and training efficient.

**Q: What does `model(x)[:, -1, :]` mean? (Last timestep output)**  
A: It means I take the output from the last timestep of the sequence, because the final state contains the most recent temporal context for the prediction.


---

### 👤 Member 3 — Health Score, AWD & Carbon Credits

**Primary Responsibility:** Multi-factor health scoring, sustainability analytics, and carbon credit estimation.

| Area | Details |
|------|---------|
| **Modules Owned** | `ml_engine/health_score.py`, `ml_engine/awd.py`, `ml_engine/cc.py`, `ml_engine/registry.py` |
| **Key Work** | Weighted ensemble fusion formula, AWD state machine detection, IPCC Tier-2 carbon calculations, model registry |
| **Key Formula** | `HS = 0.30×CNN + 0.25×NDVI + 0.20×(1-Risk) + 0.15×Weather + 0.10×Practice` |
| **Constants** | EF_continuous=1.30, EF_AWD=0.55, GWP100=27.9, Carbon=$15/tCO2e |

**Must-Know Viva Questions:**
- Explain the health score formula — why these specific weights?
- How is weather score derived from temperature, rainfall, soil moisture?
- What is AWD? How do you detect it from NDWI time series?
- Explain the IPCC Tier-2 methodology for methane calculation
- What is GWP100? Why is CH4 = 27.9× CO2?
- How does the Model Registry work? What is SHA-256 integrity verification?
- What is the Singleton design pattern? Where is it used?
- How are carbon credits valued? ($15/tonne × ₹83)
- What happens when one component is unavailable? (Graceful fallback)

### 4.7 Suggested Answers — Member 3

**Q: Explain the health score formula — why these specific weights?**  
A: The score gives the highest weight to image-based disease detection and NDVI because they are the strongest direct indicators of crop condition. Risk, weather, and practice are added as supporting signals so the score remains balanced.

**Q: How is weather score derived from temperature, rainfall, soil moisture?**  
A: The weather score measures how close the current conditions are to the crop's preferred range. If temperature, rainfall, and soil moisture are near optimal values, the score is higher.

**Q: What is AWD? How do you detect it from NDWI time series?**  
A: AWD is Alternate Wetting and Drying, a water-saving irrigation method for rice. I detect it by tracking wet and dry transitions in the NDWI series and checking whether the field repeatedly moves through drying cycles.

**Q: Explain the IPCC Tier-2 methodology for methane calculation**  
A: I use emission factors for continuous flooding and AWD, then convert methane reduction into CO2-equivalent using the GWP factor. That gives a standard, explainable carbon-credit estimate.

**Q: What is GWP100? Why is CH4 = 27.9x CO2?**  
A: GWP100 is the warming impact of a gas over 100 years. Methane has a much higher warming effect than carbon dioxide, so the factor 27.9 converts methane emissions into CO2-equivalent impact.

**Q: How does the Model Registry work? What is SHA-256 integrity verification?**  
A: The registry stores metadata for each model version and verifies the model file hash. SHA-256 ensures the file has not been corrupted or changed unexpectedly.

**Q: What is the Singleton design pattern? Where is it used?**  
A: Singleton ensures one shared instance of the registry or manager is used across the app. That keeps model metadata consistent and avoids duplicate model tracking.

**Q: How are carbon credits valued? ($15/tonne x 83 INR)**  
A: I estimate carbon credits in tonne CO2e and multiply by the assumed market price in dollars, then convert to INR. That makes the output easy to explain to farmers and evaluators.

**Q: What happens when one component is unavailable? (Graceful fallback)**  
A: The system falls back to neutral or partial inputs instead of failing the whole score. That keeps the app usable even when one data source is temporarily missing.


---

### 👤 Member 4 — Backend API & Database

**Primary Responsibility:** Django backend, REST API design, authentication, database models, and security.

| Area | Details |
|------|---------|
| **Modules Owned** | `KrishiSaarthi/settings.py`, `field/models.py`, `field/serializers.py`, `field/views/field_crud.py`, `field/views/logs_alerts.py`, `config/`, `middleware/` |
| **Key Work** | Django ORM models, DRF serializers/views, Token auth, rate limiting, CORS, PII encryption (Fernet), database design |
| **APIs** | All CRUD endpoints — field data, logs, alerts, irrigation scheduling |
| **Security** | Rate limiting, IDOR prevention, user-scoped queries, input sanitization |

**Must-Know Viva Questions:**
- Explain the Django project structure (apps, settings, URLs)
- What is Django REST Framework? Serializers vs Views vs ViewSets?
- How does Token authentication work?
- How do you prevent IDOR (Insecure Direct Object Reference)?
- What is CORS and why is it needed?
- Database schema — explain FieldData, Pest, Alert, Cost, Revenue models
- How is PII encrypted at rest? (Fernet symmetric encryption)
- What is rate limiting and how is it implemented?
- Explain `select_related` and `prefetch_related` (query optimization)
- What are Django migrations and why do they matter?

### 4.8 Suggested Answers — Member 4

**Q: Explain the Django project structure (apps, settings, URLs)**  
A: The project is split into focused apps like field, finance, planning, chat, and config. Settings manage global behavior, while URLs route requests into the right app views.

**Q: What is Django REST Framework? Serializers vs Views vs ViewSets?**  
A: DRF is Django's API toolkit. Serializers convert model data to JSON and back, views handle request logic, and viewsets combine common CRUD operations into a reusable structure.

**Q: How does Token authentication work?**  
A: After login, the backend returns a token that the frontend sends in the Authorization header on each request. The backend verifies that token and ties the request to the correct user.

**Q: How do you prevent IDOR (Insecure Direct Object Reference)?**  
A: Every query is filtered by the logged-in user, and object access is always checked against ownership. That stops one user from reading or modifying another user's records.

**Q: What is CORS and why is it needed?**  
A: CORS controls which frontend origins can call the API. It is needed because the frontend and backend run on different ports or domains during development and deployment.

**Q: Database schema — explain FieldData, Pest, Alert, Cost, Revenue models**  
A: FieldData stores polygon and crop information, Pest stores scan history and predictions, Alert stores action items, and Cost/Revenue capture finance data for season-wise reporting.

**Q: How is PII encrypted at rest? (Fernet symmetric encryption)**  
A: Sensitive fields are encrypted before storage using Fernet. That means bank or identity-like data is not stored in plain text in the database.

**Q: What is rate limiting and how is it implemented?**  
A: Rate limiting caps how many requests a user or IP can make in a short period. It protects the APIs from abuse and prevents heavy endpoints from being overwhelmed.

**Q: Explain `select_related` and `prefetch_related` (query optimization)**  
A: `select_related` uses SQL joins for one-to-one or foreign key data, while `prefetch_related` fetches many-to-many or reverse relations separately and combines them in Python. Both reduce query count.

**Q: What are Django migrations and why do they matter?**  
A: Migrations are versioned database schema changes. They matter because they let the team evolve tables safely and reproducibly as models change.


---

### 👤 Member 5 — Frontend & UI/UX

**Primary Responsibility:** React frontend — components, state management, maps, charts, and user experience.

| Area | Details |
|------|---------|
| **Modules Owned** | `frontend/client/src/components/` (all 79 files), `pages/`, `context/`, `hooks/`, `lib/` |
| **Key Work** | React 18 components, TypeScript, TailwindCSS 4, Shadcn UI, Leaflet maps, Recharts visualizations, dark/light theme, responsive design |
| **State Management** | TanStack React Query (server state), React Context (auth, field, theme) |
| **Key Features** | Interactive field mapping (polygon drawing), NDVI charts, health score dashboard, finance P&L, chatbot UI |

**Must-Know Viva Questions:**
- Why React 18? What are hooks? Explain useState, useEffect, useContext
- What is TypeScript and why use it over JavaScript?
- How does TanStack React Query manage server state?
- Explain the component architecture — layout, pages, feature modules
- How does Leaflet integration work for field polygon drawing?
- What is Vite and why is it faster than Webpack?
- How does the dark/light theme toggle work? (next-themes)
- Explain the API client — how frontend communicates with backend
- What is Shadcn UI? How is it different from Material UI?
- How do you handle responsive design for mobile vs desktop?

### 4.9 Suggested Answers — Member 5

**Q: Why React 18? What are hooks? Explain useState, useEffect, useContext**  
A: React 18 gives a modern component model and better rendering behavior. Hooks let functional components manage state, side effects, and shared context without class components.

**Q: What is TypeScript and why use it over JavaScript?**  
A: TypeScript adds static typing, which catches many bugs earlier and makes shared data contracts easier to maintain in a large app.

**Q: How does TanStack React Query manage server state?**  
A: React Query handles caching, background refetching, request deduplication, and loading states for data fetched from the backend.

**Q: Explain the component architecture — layout, pages, feature modules**  
A: The app separates page shells, feature modules, shared UI components, and hooks so each concern stays isolated and reusable.

**Q: How does Leaflet integration work for field polygon drawing?**  
A: Leaflet renders the map, captures clicks for polygon points, and stores the drawn coordinates as a field boundary that can be saved and reused.

**Q: What is Vite and why is it faster than Webpack?**  
A: Vite uses native ES modules in development and performs faster transforms, so startup and hot reload are much quicker than traditional bundlers.

**Q: How does the dark/light theme toggle work? (next-themes)**  
A: Theme state is managed centrally and applied as a class on the document. Tailwind then switches colors using CSS variables.

**Q: Explain the API client — how frontend communicates with backend**  
A: The frontend uses a shared API wrapper for authenticated GET, POST, PUT, PATCH, and DELETE calls, with caching and consistent error handling.

**Q: What is Shadcn UI? How is it different from Material UI?**  
A: Shadcn UI provides accessible, copyable component primitives styled with Tailwind. It gives more design control than a heavy opinionated component library.

**Q: How do you handle responsive design for mobile vs desktop?**  
A: Layouts use flexible grids, stacking behavior, and component spacing that adapts at breakpoints so the app stays usable on small screens and large monitors.


---

### 👤 Member 6 — Earth Engine, Chat/AI & DevOps

**Primary Responsibility:** Google Earth Engine integration, Gemini chatbot, weather APIs, deployment, and CI/CD.

| Area | Details |
|------|---------|
| **Modules Owned** | `field/services/ee_service.py`, `field/utils.py`, `field/views/weather.py`, `field/views/yield_prediction.py`, `field/views/soil_advice.py`, `chat/views.py`, `docker-compose.yml`, `.github/workflows/` |
| **Key Work** | Earth Engine satellite data (NDVI, EVI, SAVI, NDWI), Gemini 2.5 Flash chatbot, weather API integration, Docker containerization, Nginx, CI/CD pipeline |
| **External APIs** | Google Earth Engine, Google Gemini AI, OpenWeather |
| **DevOps** | Docker, Gunicorn, Nginx, GitHub Actions, Prometheus/Grafana |

**Must-Know Viva Questions:**
- What is Google Earth Engine? How does it compute vegetation indices?
- Explain NDVI, EVI, SAVI, NDWI — formulas and differences
- How does the Gemini chatbot work? Explain system prompt and context window
- How is chat history managed? (Session-based, max 20 messages)
- What is UTM projection? Why is it needed for area calculation?
- How does Docker containerization work? Explain multi-service compose
- What is Nginx and why is it used as a reverse proxy?
- Explain the CI/CD pipeline — linting, testing, Docker build
- How does the yield prediction endpoint work?
- What is Gunicorn and why not use Django's dev server in production?

### 4.10 Suggested Answers — Member 6

**Q: What is Google Earth Engine? How does it compute vegetation indices?**  
A: Google Earth Engine is a cloud geospatial platform for satellite analysis. It processes imagery over the selected polygon and computes indices like NDVI, EVI, SAVI, and NDWI from spectral bands.

**Q: Explain NDVI, EVI, SAVI, NDWI — formulas and differences**  
A: NDVI measures greenness, EVI improves sensitivity in dense vegetation, SAVI reduces soil background effects, and NDWI highlights water content or wetness.

**Q: How does the Gemini chatbot work? Explain system prompt and context window**  
A: The chatbot uses Gemini with an agriculture-focused system prompt, and the context window keeps recent conversation turns so replies stay relevant.

**Q: How is chat history managed? (Session-based, max 20 messages)**  
A: History is stored per user session and trimmed to a limited message count so the conversation remains context-aware without becoming too large or slow.

**Q: What is UTM projection? Why is it needed for area calculation?**  
A: UTM converts coordinates into a planar coordinate system, which makes polygon area calculations much more accurate than using raw latitude and longitude.

**Q: How does Docker containerization work? Explain multi-service compose**  
A: Docker packages the backend, frontend, and supporting services into isolated containers. Compose defines how those services run together with shared networking and environment variables.

**Q: What is Nginx and why is it used as a reverse proxy?**  
A: Nginx sits in front of the app, serves static assets efficiently, and forwards dynamic requests to the application server.

**Q: Explain the CI/CD pipeline — linting, testing, Docker build**  
A: The pipeline validates code through tests and build checks, then packages the app into containers so deployment remains repeatable and less error-prone.

**Q: How does the yield prediction endpoint work?**  
A: It fetches real or fallback NDVI time-series data, estimates crop yield from the NDVI trend and crop model, and returns yield plus recommendations.

**Q: What is Gunicorn and why not use Django's dev server in production?**  
A: Gunicorn is a production-grade WSGI server. Django's dev server is not designed for performance, concurrency, or security in deployment.


---

### 📋 Cross-Knowledge Matrix

> Every member should be able to answer **at least 2 basic questions** from each other member's domain.

| Member | Must Also Know (from others) |
|--------|------------------------------|
| **M1 (CNN)** | What LSTM does (M2), Health Score formula (M3), How API serves predictions (M4) |
| **M2 (LSTM)** | What CNN classifies (M1), How health score uses risk (M3), What NDVI is (M6) |
| **M3 (Health/AWD)** | CNN output format (M1), LSTM risk levels (M2), How frontend shows score (M5) |
| **M4 (Backend)** | ML model lazy loading pattern (M1/M2), Frontend API calls (M5), Docker deploy (M6) |
| **M5 (Frontend)** | What data backend returns (M4), Health score breakdown display (M3), Map/EE data (M6) |
| **M6 (EE/DevOps)** | CNN/LSTM models overview (M1/M2), API endpoints list (M4), UI components (M5) |

### 🎯 Viva Strategy

1. **First 2 minutes**: Anyone should be able to give the full project overview
2. **Deep dive**: Examiner will ask each member about their primary module
3. **Cross-questions**: Expect "How does YOUR module connect to Member X's work?"
4. **Demo**: Member 5 (Frontend) drives the demo, others explain their module when shown
5. **Tricky questions**: Member 3 (Health Score) and Member 6 (EE) often get formula/concept questions

---

*Document prepared for Capstone Viva Examination. All technical details sourced from actual codebase.*
