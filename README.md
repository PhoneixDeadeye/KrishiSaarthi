# 🌾 AgriSmart - Intelligent Agriculture Management Platform

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.1+-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/tailwindcss-4.0+-38B2AC.svg)](https://tailwindcss.com/)
[![PyTorch](https://img.shields.io/badge/pytorch-2.0+-EE4C2C.svg)](https://pytorch.org/)

**A production-ready, AI-powered agricultural management platform leveraging satellite imagery, machine learning, and real-time analytics to revolutionize farming operations.**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Reference](#-api-reference) • [Deployment](#-deployment)

</div>

---

## 🎯 Overview

AgriSmart (formerly KrishiSaarthi) is a comprehensive farm management system built for the modern farmer. It combines satellite imagery analysis, deep learning models, financial tracking, and AI-powered insights to provide actionable intelligence for agricultural decision-making.

### Why AgriSmart?

| Challenge | Solution |
|-----------|----------|
| Crop health monitoring is manual and time-consuming | 🛰️ Automated satellite-based vegetation analysis (NDVI, EVI, SAVI) |
| Pest detection requires expert knowledge | 🔬 CNN-based pest detection with Gemini Vision validation |
| Financial tracking is scattered | 💰 Integrated cost, revenue, and P&L management |
| Planning and scheduling is complex | 📅 Season calendar, equipment booking, labor management |
| Weather impacts are unpredictable | 🌤️ Real-time weather integration and forecasting |
| Carbon credit opportunities are missed | 🌱 AWD-based methane reduction and carbon credit estimation |

---

## ✨ Features

### 🛰️ Satellite & Remote Sensing
- **Google Earth Engine Integration** - Real-time vegetation indices (NDVI, EVI, SAVI, NDWI)
- **Time-Series Analysis** - Historical crop health trends and anomaly detection
- **Soil Moisture Monitoring** - Track soil conditions across your fields
- **Rainfall Analysis** - Historical precipitation data and patterns

### 🤖 Machine Learning & AI
| Model | Purpose | Technology |
|-------|---------|------------|
| **Pest Detection CNN** | Identify crop diseases from images | MobileNetV2, PyTorch |
| **Risk Prediction LSTM** | Forecast pest/disease outbreaks | LSTM, Time-series |
| **Health Score Engine** | Multi-parameter crop assessment | Ensemble (CNN + NDVI + Risk) |
| **Yield Prediction** | Estimate harvest yields | Regression models |
| **Gemini Vision Validation** | Verify plant images before analysis | Google Gemini 2.0 |

### 💬 AI-Powered Assistant
- **Agricultural Chatbot** - Gemini-powered expert advice
- **Multi-lingual Support** - English, Hindi, Punjabi, Malayalam
- **Context-Aware Responses** - Understands your farm's specific conditions
- **Voice Input** - Speak your questions naturally

### 📊 Field Management
| Feature | Description |
|---------|-------------|
| **Interactive Mapping** | Draw field boundaries on satellite imagery |
| **Activity Logging** | Track watering, fertilizer, sowing, harvesting |
| **Smart Alerts** | Automated reminders based on activities |
| **Multi-Field Support** | Manage multiple fields from one dashboard |

### 💰 Financial Management
- **Cost Tracking** - Seeds, fertilizer, labor, equipment expenses
- **Revenue Recording** - Sales, crop prices, buyer information
- **Season-Based Analysis** - Track profitability per growing season
- **P&L Dashboard** - Real-time profit/loss visualization
- **Market Prices** - Live commodity prices from major markets
- **Price Forecasting** - AI-predicted price trends (7-60 days)
- **Government Schemes** - Discover subsidies and support programs
- **Insurance Claims** - Track and manage crop insurance

### 📅 Planning & Resources
| Module | Capabilities |
|--------|-------------|
| **Season Calendar** | Plan planting and harvesting schedules |
| **Crop Rotation** | Optimize multi-season crop planning |
| **Inventory Tracker** | Manage seeds, fertilizers, pesticides, tools |
| **Labor Manager** | Schedule workers, track wages, manage attendance |
| **Equipment Scheduler** | Book tractors, harvesters, irrigation equipment |

### 🌱 Sustainability
- **Carbon Credit Estimation** - Calculate carbon sequestration potential
- **AWD Detection** - Validate Alternate Wetting & Drying practices
- **Methane Reduction Tracking** - Quantify emission reductions
- **IPCC Methodology** - Industry-standard calculations

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Google Earth Engine | Account | Satellite data |
| Gemini API Key | - | AI features |
| OpenWeather API | Optional | Weather data |

### One-Command Setup (Windows)

```powershell
# Clone the repository
git clone https://github.com/yourusername/agrismart.git
cd agrismart

# Run setup script
.\setup.ps1

# Configure environment
# Edit backend/.env with your API keys

# Start development servers
.\dev.ps1
```

### Manual Setup

#### Backend

```bash
# Navigate and create virtual environment
cd backend
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# - GEMINI_API_KEY (required)
# - OPENWEATHER_API_KEY (optional)
# - DJANGO_SECRET_KEY (required for production)

# Authenticate Earth Engine
earthengine authenticate

# Initialize database
python init_db.py

# Run server
python manage.py runserver
```

#### Frontend

```bash
cd frontend/client

# Install dependencies
npm install

# Configure API endpoint (optional)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

#### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| Admin Panel | http://localhost:8000/admin |

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React 18 + TypeScript + TailwindCSS 4 + Vite            │  │
│  │  • 21 Dashboard Features    • Real-time Charts           │  │
│  │  • Interactive Maps         • Multi-language Support     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Django 5.1 + Django REST Framework                      │  │
│  │  • Token Authentication    • CORS Configuration          │  │
│  │  • Rate Limiting           • Request Validation          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   FIELD MODULE  │  │  FINANCE MODULE │  │ PLANNING MODULE │
│ • EE Analysis   │  │ • Cost Tracking │  │ • Calendar      │
│ • Health Score  │  │ • Revenue       │  │ • Inventory     │
│ • Pest Detect   │  │ • P&L Dashboard │  │ • Labor         │
│ • Irrigation    │  │ • Market Prices │  │ • Equipment     │
│ • Alerts        │  │ • Forecasting   │  │ • Rotation      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML/AI LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ MobileNetV2 │  │ LSTM Risk   │  │ Gemini 2.5 Flash       │  │
│  │ Pest CNN    │  │ Prediction  │  │ • Image Validation     │  │
│  │ 9.1MB Model │  │ Time-Series │  │ • Chat Assistant       │  │
│  └─────────────┘  └─────────────┘  │ • Soil Advice          │  │
│                                     └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Google      │  │ OpenWeather │  │ Google Gemini AI       │  │
│  │ Earth Engine│  │ API         │  │ (Vision + Chat)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
AgriSmart/
├── backend/                      # Django REST API Backend
│   ├── KrishiSaarthi/           # Django project settings
│   │   ├── settings.py          # Configuration
│   │   └── urls.py              # Root URL routing
│   ├── field/                   # Field management app
│   │   ├── models.py            # FieldData, Pest, Alert models
│   │   ├── views/               # API view classes
│   │   │   ├── analysis.py      # EE, Pest, AWD, CarbonCredit
│   │   │   ├── data.py          # Field CRUD operations
│   │   │   ├── logs_alerts.py   # Activity logging, alerts
│   │   │   ├── weather.py       # Weather integration
│   │   │   ├── irrigation.py    # Irrigation scheduling
│   │   │   └── yield_prediction.py
│   │   ├── serializers.py       # API serializers
│   │   └── utils.py             # Earth Engine utilities
│   ├── finance/                 # Financial management app
│   │   ├── models.py            # Cost, Revenue, Season models
│   │   └── views/               # Cost, P&L, Market, Forecast
│   ├── planning/                # Resource planning app
│   │   ├── models.py            # Calendar, Inventory, Labor, Equipment
│   │   └── views/               # Planning API endpoints
│   ├── chat/                    # AI assistant app
│   │   └── views.py             # Gemini chat integration
│   ├── ml_engine/               # Machine learning module
│   │   ├── cnn.py               # MobileNetV2 pest detection
│   │   ├── lstm.py              # Risk prediction model
│   │   ├── health_score.py      # Multi-factor health scoring
│   │   └── awd.py               # AWD detection from NDWI
│   └── ml_models/               # Trained model weights
│       ├── crop_health_model.pth   # 9.1MB CNN model
│       ├── risk_lstm_final.pth     # LSTM weights
│       └── risk_scaler.save        # Input normalization
│
├── frontend/                     # React TypeScript Frontend
│   └── client/
│       ├── src/
│       │   ├── components/      # UI Components (79 files)
│       │   │   ├── analytics/   # DataAnalytics, IndicesReport
│       │   │   ├── chat/        # ChatBot
│       │   │   ├── dashboard/   # HomeDashboard, Widgets
│       │   │   ├── field/       # FieldReport, Pest, Irrigation
│       │   │   ├── finance/     # CostCalculator, PnL, Market
│       │   │   ├── planning/    # Calendar, Inventory, Labor
│       │   │   ├── layout/      # Sidebar, TopBar, Theme
│       │   │   └── ui/          # Shadcn UI components
│       │   ├── pages/           # Dashboard, Landing, Auth
│       │   ├── context/         # Auth, Field, Theme providers
│       │   ├── hooks/           # useTranslation, useVoice
│       │   ├── lib/             # API client, utilities
│       │   └── types/           # TypeScript interfaces
│       └── tailwind.config.js   # Custom design tokens
│
├── docker-compose.yml           # Development orchestration
├── docker-compose.prod.yml      # Production orchestration
├── nginx/                       # Nginx configuration
└── monitoring/                  # Prometheus/Grafana configs
```

---

## 📡 API Reference

### Authentication

All protected endpoints require token authentication:

```http
Authorization: Token <your-token-here>
```

### Endpoint Categories

#### 🔐 Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | User login, returns token |
| POST | `/signup` | User registration |
| POST | `/logout` | Invalidate token |
| POST | `/password-reset` | Request reset email |
| POST | `/password-reset-confirm` | Complete reset |

#### 🗺️ Field Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/field/data` | List user's fields |
| POST | `/field/set_polygon` | Create/update field |
| DELETE | `/field/data/<id>` | Delete field |
| GET | `/field/coord` | Get field coordinates |

#### 📊 Analysis & ML
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/field/ee` | Earth Engine vegetation analysis |
| GET | `/field/healthscore` | Crop health score (0-100) |
| GET | `/field/pestpredict` | Pest risk prediction |
| POST | `/field/pest/report` | Upload pest image (with Gemini validation) |
| GET | `/field/awd` | AWD detection status |
| GET | `/field/cc` | Carbon credit estimation |
| GET | `/field/yield-prediction` | Yield forecast |
| POST | `/field/soil-advice` | AI soil management advice |

#### 📝 Logs & Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/field/logs` | Field activity history |
| POST | `/field/logs` | Log new activity |
| GET | `/field/alerts` | Pending alerts |
| PATCH | `/field/alerts/<id>` | Mark alert as read |

#### 💧 Irrigation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/field/irrigation-schedule` | Get schedule |
| POST | `/field/irrigation-schedule` | Create schedule event |
| GET | `/field/irrigation-logs` | Irrigation history |

#### 💰 Finance
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/finance/costs` | Cost entries CRUD |
| GET | `/finance/costs/summary` | Cost totals by category |
| GET/POST | `/finance/revenue` | Revenue entries CRUD |
| GET/POST | `/finance/seasons` | Season management |
| GET | `/finance/pnl` | Profit & Loss dashboard |
| GET | `/finance/market-prices` | Live commodity prices |
| GET | `/finance/price-forecast` | AI price predictions |
| GET | `/finance/schemes` | Government schemes |
| GET/POST | `/finance/insurance` | Insurance claims |

#### 📅 Planning
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/planning/calendar` | Season calendar events |
| GET/POST | `/planning/inventory` | Inventory items CRUD |
| GET/POST | `/planning/labor` | Labor entries |
| GET/POST | `/planning/equipment` | Equipment bookings |
| GET/POST | `/planning/rotation` | Crop rotation plans |

#### 💬 Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/api/a` | AI assistant query |
| GET | `/chat/api/history/<session_id>` | Chat history |

#### 🏥 Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check |

---

## 🔧 Configuration

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | ✅ | - | Django cryptographic key |
| `DEBUG` | ❌ | `True` | Debug mode (False in production) |
| `ALLOWED_HOSTS` | ❌ | `localhost,127.0.0.1` | Permitted hosts |
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `OPENWEATHER_API_KEY` | ❌ | - | OpenWeather API key |
| `DATABASE_URL` | ❌ | SQLite | PostgreSQL connection string |
| `CORS_ALLOWED_ORIGINS` | ❌ | `http://localhost:5173` | Frontend origins |

#### Frontend (`frontend/client/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |

---

## 🐳 Docker Deployment

### Development

```bash
# Build and start all services
docker-compose up --build

# Initialize database (first time)
docker-compose exec backend python init_db.py
```

### Production

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# With SSL/TLS
# Configure nginx/nginx.conf with your certificates
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 80 | Nginx serving React app |
| backend | 8000 | Django + Gunicorn |
| db | 5432 | PostgreSQL (production) |

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend/client
npm test

# E2E tests
npm run test:e2e
```

---

## 🔬 ML Models

### Pre-trained Weights

| Model | File | Size | Purpose |
|-------|------|------|---------|
| Pest Detection | `crop_health_model.pth` | 9.1 MB | MobileNetV2 binary classifier |
| Risk Prediction | `risk_lstm_final.pth` | 208 KB | LSTM time-series model |
| Input Scaler | `risk_scaler.save` | 711 B | Feature normalization |

### Model Details

#### Pest Detection CNN
- **Architecture**: MobileNetV2 with custom classifier
- **Input**: 224x224 RGB images
- **Output**: Probability 0-1 (>0.5 = Healthy)
- **Validation**: Gemini Vision pre-validates plant images

#### Risk Prediction LSTM
- **Architecture**: 2-layer LSTM
- **Input**: 14-day time-series (NDVI, weather, activity)
- **Output**: Risk score 0-100

---

## 🌍 Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS 4, Shadcn UI, Leaflet, Recharts |
| **Backend** | Django 5.1, Django REST Framework, PyTorch, Python 3.11+ |
| **AI/ML** | Google Gemini 2.5 Flash, MobileNetV2, LSTM, Scikit-learn |
| **Data** | Google Earth Engine, OpenWeather API, PostgreSQL/SQLite |
| **DevOps** | Docker, Nginx, Gunicorn, GitHub Actions |

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

### Quick Fixes

| Issue | Solution |
|-------|----------|
| Earth Engine auth failed | Run `earthengine authenticate` |
| ML models not loading | Verify `.pth` files in `backend/ml_models/` |
| CORS errors | Check `CORS_ALLOWED_ORIGINS` in `.env` |
| Database errors | Run `python manage.py migrate --run-syncdb` |

---

## 📧 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/agrismart/issues)
- 💬 [Discussions](https://github.com/yourusername/agrismart/discussions)

---

## 🙏 Acknowledgments

- [Google Earth Engine](https://earthengine.google.com/) - Satellite data platform
- [Google Gemini](https://ai.google.dev/) - AI capabilities
- [OpenWeather](https://openweathermap.org/) - Weather data
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Shadcn UI](https://ui.shadcn.com/) - Component library

---

<div align="center">

**Built with 💚 for farmers worldwide**

*Empowering agriculture through technology*

</div>
