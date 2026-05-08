# KrishiSaarthi (AgriSmart) — Complete Technical & Product Report

**Version:** 1.0  
**Date:** 2026-04-11  
**Status:** Implementation-Ready  

---

## 1. PROJECT OVERVIEW

### 1.1 Vision Statement

KrishiSaarthi is an AI-driven, full-stack farm and crop management ecosystem designed for Indian smallholder farmers, agricultural extension officers, and agri-professionals. It integrates satellite remote sensing (Google Earth Engine), deep-learning models (CNN for pest/disease detection, LSTM for risk prediction), weather APIs, and a Gemini-powered conversational assistant into a single Progressive Web App. The platform solves the problem of fragmented, paper-based farm management by providing real-time crop health monitoring, precision irrigation scheduling, financial P&L tracking, government scheme discovery, market price intelligence, and actionable alerts—all accessible via a mobile-friendly browser on low-bandwidth networks. Success looks like: a farmer opens the dashboard, sees their field's satellite-derived health score, receives a pest alert with diagnosis and treatment advice, logs irrigation, tracks costs, and gets a profitability report—all within a single session.

### 1.2 Goals & Success Metrics

| # | Goal | KPI | Target |
|---|------|-----|--------|
| 1 | Real-time crop health monitoring | Health score accuracy vs ground truth | ≥ 78% |
| 2 | Fast API responses | P95 API latency (non-ML endpoints) | < 300 ms |
| 3 | ML inference reliability | CNN pest detection accuracy (PlantVillage) | ≥ 92.8% |
| 4 | Risk prediction | LSTM risk prediction AUC | ≥ 0.85 |
| 5 | Uptime | Application availability | 99.5% |
| 6 | Mobile usability | Lighthouse Performance score | ≥ 70 |
| 7 | Data freshness | Satellite data update frequency | Daily |
| 8 | User engagement | Fields created per active user | ≥ 1 |

### 1.3 Scope

**IN SCOPE:**
- User authentication (signup, login, password reset, email verification, token-based sessions)
- Multi-field management with GeoJSON polygon mapping via Leaflet
- Google Earth Engine integration for NDVI, EVI, SAVI, NDWI, soil moisture, temperature, and rainfall time series
- CNN-based crop disease/pest detection from uploaded images (MobileNetV2, 38 classes)
- LSTM-based crop risk prediction from NDVI/weather time series
- Multi-factor health score fusion (satellite + CNN + LSTM)
- Alternate Wetting & Drying (AWD) irrigation detection from NDWI series
- Carbon credit estimation from AWD practices and area
- Weather integration via OpenWeatherMap API
- Soil health advice generation via Gemini AI
- Yield prediction using regional/crop statistical models
- Crop rotation planning with agronomic compatibility rules
- Irrigation scheduling and logging
- Field activity logging and automated alerting
- Financial tracking: cost entries, revenue entries, seasons, P&L dashboard
- Market price lookup via data.gov.in / Agmarknet
- LSTM-based price forecasting
- Government scheme matching with eligibility filtering
- Crop insurance claim management (PMFBY workflow)
- Farm inventory management with stock tracking and transaction history
- Labor worker management with wage calculation
- Equipment registry and booking with overlap prevention
- Season calendar for farm activity planning
- AI chatbot (Gemini 2.5 Flash) with conversation history
- PDF/Excel export of reports
- Dark/light theme support
- Multi-language support infrastructure (Hindi/English)
- Voice recording input for chat
- Progressive Web App (installable, offline shell)
- Docker Compose deployment with PostgreSQL, Redis, Celery
- Prometheus metrics + health/readiness endpoints
- API documentation via Swagger/ReDoc (drf-spectacular)

**OUT OF SCOPE:**
- Native mobile applications (iOS/Android)
- Real-time WebSocket push notifications (polling is used)
- Payment gateway integration
- Hardware IoT sensor integration
- Drone imagery processing
- Multi-tenant SaaS billing
- Offline-first data sync (PWA caches static shell only)
- Community/social features between farmers

### 1.4 Assumptions & Constraints

**Assumptions:**
- Users have intermittent internet access (≥ 2G) and modern mobile browsers
- Google Earth Engine service account credentials are provisioned with EE API scope
- A valid Gemini API key is available for chatbot and image validation
- An OpenWeatherMap API key is available for weather data
- PlantVillage-trained CNN model weight files are pre-deployed to `backend/ml_models/`
- PostgreSQL 15+ is used in production; SQLite is acceptable for local development
- Redis 7+ is available for caching and Celery task brokering

**Constraints:**
- All monetary values are in Indian Rupees (₹)
- Satellite imagery has a 5-day revisit period (Sentinel-2) and 250m resolution (MODIS)
- ML inference endpoints (pest detection, health score) are computationally expensive, capped at 30 req/hour per user
- Gemini chat is capped at 60 req/hour per user
- Earth Engine requests are capped at 20 req/hour per user
- Maximum image upload size: 10 MB (JPEG/PNG only)
- Maximum chat question length: 4000 characters
- Maximum chat sessions per user: 50 (oldest auto-deleted)
- Knox auth tokens have configurable TTL; frontend has a 30-minute inactivity timeout

---

## 2. USERS & ROLES

### 2.1 Farmer (Standard User)

| Attribute | Detail |
|-----------|--------|
| **Description** | A smallholder or commercial farmer managing one or more fields. Primary consumer of all features. |
| **Registration** | Self-service via `/signup` form (username, email, password). Optional email verification in production. |
| **Permissions** | Full CRUD on own fields, logs, alerts, costs, revenues, seasons, inventory, labor, equipment, bookings, calendar events, insurance claims. Read-only access to government schemes. Full access to all ML endpoints and chatbot. Cannot access other users' data. Cannot access admin panel or metrics endpoint. |
| **Key Workflows** | 1) Add a field by drawing a polygon on the map → 2) View satellite health report → 3) Upload pest image for diagnosis → 4) Log irrigation event → 5) Track costs and revenue → 6) View P&L dashboard → 7) Discover government schemes → 8) Chat with AI assistant |

### 2.2 Admin (Superuser)

| Attribute | Detail |
|-----------|--------|
| **Description** | System administrator with Django admin access. Manages users, scheme data, and system health. |
| **Registration** | Created via `manage.py createsuperuser` or `init_db.py` script. |
| **Permissions** | All farmer permissions across all users. Access to Django admin panel at `/admin/`. Access to `/metrics` endpoint. Can create/edit/delete GovernmentScheme records. Can view all users and their data. |
| **Key Workflows** | 1) Populate government scheme database → 2) Monitor system health via `/health`, `/ready`, `/metrics` → 3) Review and manage user accounts → 4) Moderate insurance claims |

### 2.3 Guest (Unauthenticated)

| Attribute | Detail |
|-----------|--------|
| **Description** | Any visitor who has not logged in. |
| **Permissions** | Can view the landing page (`/`). Can access `/login`, `/signup`, `/forgot-password`, `/reset-password/:uid/:token`. Can access `/health` and `/ready` endpoints. Cannot access any authenticated features. |
| **Key Workflows** | 1) View landing page → 2) Register or login |

---

## 3. SYSTEM ARCHITECTURE

### 3.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│  React 18 + Vite 7 + TailwindCSS 3 + Leaflet + Recharts     │
│  PWA Service Worker · Dark/Light Theme · Hindi/English       │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS / Vite Proxy (dev: 5173→8000)
                         │ Nginx reverse proxy (prod: 80→8000)
┌────────────────────────▼─────────────────────────────────────┐
│                   BACKEND (Django 5.1 + DRF 3.16)            │
│  Gunicorn (prod) · Knox Token Auth · drf-spectacular          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  field/   │ │ finance/ │ │ planning/│ │  chat/   │        │
│  │  views    │ │  views   │ │  views   │ │  views   │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │             │            │             │              │
│  ┌────▼─────────────▼────────────▼─────────────▼────────┐    │
│  │                    ml_engine/                         │    │
│  │  CNN (MobileNetV2) · LSTM · AWD · CC · Health Score   │    │
│  └───────────────────────────────────────────────────────┘    │
└──────┬─────────────┬─────────────┬──────────────┬────────────┘
       │             │             │              │
  ┌────▼────┐  ┌─────▼─────┐ ┌────▼────┐  ┌──────▼──────┐
  │PostgreSQL│  │   Redis   │ │ Celery  │  │ File Storage│
  │  15      │  │    7      │ │ Workers │  │  (media/)   │
  └─────────┘  └───────────┘ └─────────┘  └─────────────┘

External Services:
  • Google Earth Engine API (Sentinel-2/MODIS satellite data)
  • OpenWeatherMap API (current weather + forecast)
  • Google Gemini API (chatbot + image validation)
  • data.gov.in / Agmarknet API (market prices)
```

**Frontend:** Single-page React 18 application, built with Vite 7, styled with TailwindCSS 3.4, using shadcn/ui components (Radix UI primitives). Routing via `wouter`. Map rendering via `react-leaflet`. Charts via `recharts`. PDF export via `jspdf`. PWA via `vite-plugin-pwa`. Hosted as static files served by Nginx in production.

**Backend:** Django 5.1.7 monolith with Django REST Framework 3.16. Four Django apps: `field`, `finance`, `planning`, `chat`. Separate `ml_engine` Python package for all ML inference. Separate `config` package for cross-cutting concerns (throttling, pagination, encryption, caching, logging). Custom `middleware` for request logging.

**Database:** PostgreSQL 15 (production) / SQLite (development). Stores all user data, field polygons (GeoJSON in JSONField), financial records, planning data, chat history, and insurance claims with encrypted bank account fields.

**Cache Layer:** Redis 7 used for: Django cache backend, Celery task broker and result backend, rate limiting storage, and distributed task locking (preventing concurrent Celery runs).

**External Services:**
- Google Earth Engine: Satellite vegetation indices (NDVI, EVI, SAVI, NDWI), soil moisture, temperature, rainfall
- OpenWeatherMap: Current weather conditions and 5-day forecasts
- Google Gemini AI: Conversational chatbot (gemini-2.5-flash), image validation for pest uploads (gemini-2.0-flash)
- data.gov.in / Agmarknet: Daily agricultural commodity market prices

**Background Jobs:** Celery workers running 5 periodic tasks (weather updates, satellite data refresh, risk score calculation, daily report generation, old log cleanup).

**File Storage:** Local filesystem (`media/`) for uploaded pest images and ML scan images. Served via Django's `MEDIA_URL` in dev, Nginx in prod.

### 3.2 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Framework** | React | 18.3.1 | UI component library |
| **Build Tool** | Vite | 7.1.6 | Dev server, HMR, production bundling |
| **CSS Framework** | TailwindCSS | 3.4.17 | Utility-first CSS styling |
| **Component Library** | Radix UI (shadcn/ui) | Various | Accessible, unstyled UI primitives |
| **Routing** | Wouter | 3.3.5 | Lightweight client-side routing |
| **State Management** | TanStack React Query | 5.60.5 | Server state caching and synchronization |
| **Maps** | Leaflet + react-leaflet | 1.9.4 / 4.2.1 | Interactive map rendering and polygon drawing |
| **Charts** | Recharts | 2.15.2 | Data visualization (line, bar, area, pie charts) |
| **PDF Generation** | jsPDF + jspdf-autotable | 4.0.0 / 5.0.7 | Client-side PDF report export |
| **Form Validation** | Zod + React Hook Form | 3.24 / 7.55 | Schema validation and form state |
| **Animation** | Framer Motion | 11.13.1 | Page transitions and micro-animations |
| **Geospatial** | Turf.js | 7.2.0 | Client-side area calculation and geo utilities |
| **PWA** | vite-plugin-pwa | 1.2.0 | Service worker, offline shell, installability |
| **Icons** | Material Symbols + Lucide React | — | Icon sets used across the dashboard |
| **TypeScript** | TypeScript | 5.6.3 | Static type checking |
| **Backend Framework** | Django | 5.1.7 | Python web framework |
| **REST API** | Django REST Framework | 3.16.0 | API endpoint serialization and views |
| **Authentication** | django-rest-knox | 5.0.4 | Token-based auth with per-token expiry |
| **API Docs** | drf-spectacular | 0.28.0 | OpenAPI 3.0 schema, Swagger UI, ReDoc |
| **CORS** | django-cors-headers | 4.9.0 | Cross-origin request handling |
| **Task Queue** | Celery | 5.3.6 | Async task processing |
| **Task Scheduler** | django-celery-beat | 2.7.0 | Periodic task scheduling via DB |
| **Cache/Broker** | Redis + django-redis + hiredis | 7 / 5.0.1 / 2.3.2 | Caching, Celery broker, rate limiting |
| **Database** | PostgreSQL | 15 | Primary data store (production) |
| **Database Driver** | psycopg2-binary | 2.9.9 | PostgreSQL adapter for Python |
| **ML: Deep Learning** | PyTorch + TorchVision | 2.5.1 / 0.20.1 | CNN and LSTM model inference |
| **ML: Data Science** | NumPy + Pandas + scikit-learn | 2.1.2 / 2.2.3 / 1.6.1 | Data processing, scaling, model I/O |
| **ML: Image** | Pillow | 11.3.0 | Image loading and preprocessing |
| **Satellite** | earthengine-api | 1.6.6 | Google Earth Engine Python SDK |
| **Geospatial (Python)** | Shapely + pyproj | 2.0.6 / 3.7.0 | Polygon area calculation, CRS transforms |
| **AI/LLM** | google-generativeai | 0.8.3 | Gemini API client for chat and vision |
| **Encryption** | cryptography (Fernet) | 44.0.0 | At-rest encryption for PII fields |
| **HTTP Client** | requests | 2.32.3 | External API calls (weather, market) |
| **Monitoring** | django-prometheus | — | Prometheus metrics export |
| **WSGI Server** | Gunicorn | 21.2.0 | Production-grade Python HTTP server |
| **Containerization** | Docker + Docker Compose | — | Container orchestration |
| **Reverse Proxy** | Nginx | — | Static file serving, SSL termination |
| **Testing** | pytest + pytest-django | 8.3.4 / 4.9.0 | Backend test runner |

### 3.3 Folder Structure

```
KrishiSaarthi/
├── backend/
│   ├── KrishiSaarthi/          → Django project settings, root URLs, auth views, health endpoints
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py            → Login, Signup, Logout, TestToken, PasswordReset, VerifyEmail
│   │   ├── health.py           → HealthCheck, ReadinessCheck, Metrics endpoints
│   │   └── serializers.py      → UserSerializer
│   ├── field/                  → Field management Django app
│   │   ├── models.py           → FieldData, Pest, FieldLog, FieldAlert, IrrigationLog, CropHealthScan
│   │   ├── serializers.py      → All field-related serializers
│   │   ├── validators.py       → Polygon validation rules
│   │   ├── utils.py            → fetchEEData, calculate_area_in_hectares
│   │   ├── tasks.py            → Celery background tasks
│   │   ├── urls.py             → URL routing for 18 field endpoints
│   │   ├── views/
│   │   │   ├── field_crud.py   → FieldDataView, SavePolygon, GetCoordView
│   │   │   ├── analysis.py     → EEAnalysis, PestReport, AWD, CarbonCredit, PestPrediction, HealthScore
│   │   │   ├── weather.py      → WeatherView (OpenWeatherMap proxy)
│   │   │   ├── logs_alerts.py  → FieldLogView, FieldAlertView, BulkMarkAlertsRead
│   │   │   ├── soil_advice.py  → SoilAdviceView (Gemini-powered)
│   │   │   ├── irrigation.py   → IrrigationScheduleView, IrrigationLogView
│   │   │   ├── yield_prediction.py → YieldPredictionView
│   │   │   └── diagnose.py     → DiagnoseHealthView
│   │   └── services/           → Earth Engine data fetching service layer
│   ├── finance/                → Finance management Django app
│   │   ├── models.py           → Season, CostEntry, Revenue, GovernmentScheme, InsuranceClaim, FinanceTransaction
│   │   ├── serializers.py      → All finance serializers
│   │   ├── urls.py             → URL routing for 14 finance endpoints
│   │   └── views/
│   │       ├── cost_calculator.py → CostEntryView, CostSummaryView
│   │       ├── revenue.py       → RevenueView
│   │       ├── season.py        → SeasonView
│   │       ├── pnl_dashboard.py → PnLDashboardView
│   │       ├── market_prices.py → MarketPricesView (data.gov.in proxy)
│   │       ├── price_forecast.py → PriceForecastView (LSTM-based)
│   │       ├── schemes.py       → SchemesView, SchemeDetailView
│   │       ├── insurance.py     → InsuranceClaimView, InsuranceClaimDetailView
│   │       └── transactions.py  → FinanceTransactionViewSet
│   ├── planning/               → Planning management Django app
│   │   ├── models.py           → SeasonCalendar, InventoryItem, InventoryTransaction, LaborEntry, Equipment, EquipmentBooking, Plan
│   │   ├── serializers.py      → All planning serializers
│   │   ├── urls.py             → URL routing for 14 planning endpoints
│   │   └── views/
│   │       ├── calendar.py      → SeasonCalendarView
│   │       ├── inventory.py     → InventoryItemView, InventoryTransactionView
│   │       ├── labor.py         → LaborEntryView
│   │       ├── equipment.py     → EquipmentView, EquipmentBookingView
│   │       ├── rotation.py      → RotationPlannerView (rule-based)
│   │       └── plan.py          → PlanViewSet
│   ├── chat/                   → AI chatbot Django app
│   │   ├── models.py           → ChatSession, ChatMessage
│   │   ├── serializers.py      → ChatSessionSerializer
│   │   ├── urls.py             → URL routing for chat endpoints
│   │   └── views.py            → ChatView (Gemini integration), ChatHistoryView
│   ├── ml_engine/              → Machine learning inference package
│   │   ├── __init__.py         → Lazy-loading registry for all ML exports
│   │   ├── cnn.py              → MobileNetV2-based pest/disease classification (38 classes)
│   │   ├── lstm.py             → LSTM risk prediction from time series
│   │   ├── awd.py              → AWD irrigation detection from NDWI
│   │   ├── cc.py               → Carbon credit calculation
│   │   ├── health_score.py     → Multi-factor health score fusion
│   │   └── registry.py         → Model file registry and version tracking
│   ├── config/                 → Cross-cutting configuration
│   │   ├── throttling.py       → Rate limiting classes (burst, sustained, ML, chat, EE, login)
│   │   ├── pagination.py       → Standard pagination configuration
│   │   ├── cache.py            → Redis cache configuration utilities
│   │   ├── encryption.py       → Fernet field-level encryption for PII
│   │   └── logging_config.py   → Structured logging configuration
│   ├── middleware/             → Custom Django middleware
│   │   └── request_logging.py  → HTTP request/response logging middleware
│   ├── ml_models/              → Trained model weight files (.pth, .pkl)
│   ├── media/                  → User-uploaded files (pest images, ML scans)
│   ├── tests/                  → pytest test suite
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/
│   ├── client/
│   │   ├── src/
│   │   │   ├── App.tsx          → Root component, routing, provider hierarchy
│   │   │   ├── main.tsx         → Entry point
│   │   │   ├── index.css        → Global styles and Tailwind directives
│   │   │   ├── context/
│   │   │   │   ├── AuthContext.tsx  → Authentication state, login/logout, 401 interceptor
│   │   │   │   └── FieldContext.tsx → Field state management, selected field tracking
│   │   │   ├── hooks/
│   │   │   │   ├── useWeather.ts      → Weather data fetching hook
│   │   │   │   ├── useHealthScore.ts  → Health score fetching hook
│   │   │   │   ├── useTranslation.tsx → i18n translation hook
│   │   │   │   ├── useVoiceRecording.tsx → MediaRecorder voice input hook
│   │   │   │   ├── use-toast.ts       → Toast notification hook
│   │   │   │   └── use-mobile.tsx     → Mobile breakpoint detection hook
│   │   │   ├── lib/
│   │   │   │   ├── api.ts       → API client (apiFetch, apiGet, apiPost, 401 handler, endpoints)
│   │   │   │   ├── logger.ts    → Browser-side structured logger
│   │   │   │   ├── queryClient.ts → TanStack Query client configuration
│   │   │   │   └── utils.ts     → Utility functions (cn class merger)
│   │   │   ├── pages/
│   │   │   │   ├── LandingPage.tsx   → Public marketing page
│   │   │   │   ├── LoginPage.tsx     → Login form
│   │   │   │   ├── SignupPage.tsx    → Registration form
│   │   │   │   ├── ForgotPassword.tsx→ Password reset request
│   │   │   │   ├── ResetPassword.tsx → Password reset confirmation
│   │   │   │   ├── Dashboard.tsx     → Main authenticated dashboard (sidebar + tab router)
│   │   │   │   └── not-found.tsx     → 404 page
│   │   │   ├── components/
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── HomeDashboard.tsx   → Overview cards (weather, health, market, quick actions)
│   │   │   │   │   ├── WeatherWidget.tsx   → Current weather display
│   │   │   │   │   ├── HealthGauge.tsx     → Animated health score gauge
│   │   │   │   │   └── FarmMap3D.tsx       → 3D/interactive farm map visualization
│   │   │   │   ├── field/
│   │   │   │   │   ├── MyField.tsx         → Field list + add field form
│   │   │   │   │   ├── MapView.tsx         → Leaflet map with polygon drawing/editing
│   │   │   │   │   ├── FieldReport.tsx     → Satellite indices report + charts
│   │   │   │   │   ├── EEData.tsx          → Earth Engine data display
│   │   │   │   │   ├── Pest.tsx            → Pest image upload + CNN results display
│   │   │   │   │   ├── FieldLog.tsx        → Activity log CRUD with calendar view
│   │   │   │   │   ├── FieldAlerts.tsx     → Alert list with mark-read functionality
│   │   │   │   │   ├── IrrigationScheduler.tsx → Irrigation planning + log management
│   │   │   │   │   └── YieldPrediction.tsx → Yield estimation UI with charts
│   │   │   │   ├── finance/
│   │   │   │   │   ├── CostCalculator.tsx  → Full CRUD for cost entries with category breakdown
│   │   │   │   │   ├── PnLDashboard.tsx    → Profit & Loss charts and summaries
│   │   │   │   │   ├── MarketPrices.tsx    → Live mandi price table
│   │   │   │   │   ├── PriceForecast.tsx   → Price trend charts with LSTM predictions
│   │   │   │   │   ├── SchemeMatcher.tsx   → Government scheme discovery + eligibility
│   │   │   │   │   └── InsuranceClaims.tsx → Insurance claim CRUD + status tracking
│   │   │   │   ├── planning/
│   │   │   │   │   ├── SeasonCalendar.tsx  → Calendar view with farm activity planning
│   │   │   │   │   ├── InventoryTracker.tsx→ Inventory items + transactions
│   │   │   │   │   ├── LaborManager.tsx    → Worker/wage management
│   │   │   │   │   ├── EquipmentScheduler.tsx → Equipment registry + booking
│   │   │   │   │   └── RotationPlanner.tsx → Crop rotation planning UI
│   │   │   │   ├── analytics/
│   │   │   │   │   ├── DataAnalytics.tsx   → Multi-chart analytics dashboard
│   │   │   │   │   └── IndicesReport.tsx   → Vegetation indices time series
│   │   │   │   ├── chat/
│   │   │   │   │   └── ChatBot.tsx         → Floating AI chatbot with voice input
│   │   │   │   ├── layout/
│   │   │   │   │   ├── TopBar.tsx          → Header bar component
│   │   │   │   │   └── ThemeProvider.tsx   → Dark/light mode context
│   │   │   │   ├── common/
│   │   │   │   │   ├── ErrorBoundary.tsx   → Global React error boundary
│   │   │   │   │   └── ExportButton.tsx    → PDF/Excel export functionality
│   │   │   │   └── ui/                     → shadcn/ui component library (40+ primitives)
│   │   │   └── types/
│   │   │       └── field.ts                → TypeScript type definitions
│   │   └── index.html
│   ├── vite.config.ts       → Build config, path aliases, proxy rules, PWA config
│   ├── tailwind.config.ts   → Theme customization, color palette, typography
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf           → Production reverse proxy config
├── docker-compose.yml       → Dev: backend + celery-worker + frontend + postgres + redis
├── docker-compose.prod.yml  → Prod: adds nginx, monitoring stack
└── .env.example             → Template for all environment variables
```

### 3.4 Deployment Architecture

**Environments:**

| Environment | Backend | Frontend | Database | Redis |
|------------|---------|----------|----------|-------|
| **Local Dev** | `python manage.py runserver 8000` | `npm run dev` (Vite HMR on 5173) | SQLite `db.sqlite3` | Optional (fallback to LocMem) |
| **Docker Dev** | `docker-compose up` (gunicorn on 8000) | Vite dev server on 5173 | PostgreSQL 15 container | Redis 7 container |
| **Production** | `docker-compose -f docker-compose.prod.yml up` | Nginx serves static `dist/` | PostgreSQL 15 container (persistent volume) | Redis 7 container (persistent volume) |

**Container Strategy (Docker Compose):**
- `krishisaarthi-backend`: Django + Gunicorn on port 8000
- `krishisaarthi-celery-worker`: Celery worker with concurrency=2
- `krishisaarthi-frontend`: Nginx serving built frontend on port 80
- `krishisaarthi-db`: PostgreSQL 15 Alpine with named volume
- `krishisaarthi-redis`: Redis 7 Alpine with named volume

**CI/CD Pipeline Steps:**
1. Run `pytest` backend test suite
2. Run `tsc` TypeScript check on frontend
3. Run `npm run build` to produce production bundle
4. Build Docker images
5. Push to container registry
6. Deploy to staging (run migrations, collect static)
7. Run integration tests against staging
8. Promote to production

---

## 4. DATA MODELS

### 4.1 User (Django built-in `auth.User`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | AutoField (PK) | Auto | Primary key |
| username | CharField(150) | Yes | Unique login identifier |
| email | EmailField | No | User email address |
| password | CharField | Yes | Hashed password (PBKDF2) |
| is_active | BooleanField | Yes (default: True) | Account active status |
| is_staff | BooleanField | Yes (default: False) | Admin panel access |
| date_joined | DateTimeField | Auto | Registration timestamp |

---

### 4.2 FieldData (`field.FieldData`)

**Table:** `field_fielddata`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Field owner. CASCADE on delete. |
| name | CharField(100) | No | "My Field" | User-assigned field name |
| cropType | CharField(32) | Yes | — | Active crop type (e.g., "Rice", "Wheat") |
| polygon | JSONField | Yes | — | GeoJSON polygon: `{"type": "Polygon", "coordinates": [[[lng,lat],...]]}` |
| created_at | DateTimeField | Auto | now | Creation timestamp |
| updated_at | DateTimeField | Auto | now | Last modification timestamp |

**Relationships:** Has many → FieldLog, FieldAlert, IrrigationLog, CropHealthScan, CostEntry, Revenue, Season, InsuranceClaim, SeasonCalendar, LaborEntry, EquipmentBooking, InventoryTransaction, Plan

**Indexes:** Composite index on `(user, created_at)`

**Validation:** `polygon` field validated by `validators.validate_polygon` which enforces: must be a dict with `coordinates` key, coordinates must be a list of rings, each ring must have ≥ 3 points, each point must be `[longitude, latitude]` with valid ranges.

**Example:**
```json
{
  "id": 1,
  "user": 1,
  "name": "North Paddy Field",
  "cropType": "Rice",
  "polygon": {
    "type": "Polygon",
    "coordinates": [[[75.123, 30.456], [75.124, 30.456], [75.124, 30.457], [75.123, 30.457], [75.123, 30.456]]]
  },
  "created_at": "2026-03-15T10:30:00Z",
  "updated_at": "2026-04-01T14:00:00Z"
}
```

---

### 4.3 Pest (`field.Pest`)

**Table:** `field_pest`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Uploader |
| field | ForeignKey → FieldData | No | NULL | Associated field (nullable) |
| image | ImageField | Yes | — | Uploaded image file (upload_to="pest/") |
| uploaded_at | DateTimeField | Auto | now | Upload timestamp |

---

### 4.4 FieldLog (`field.FieldLog`)

**Table:** `field_fieldlog`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Log owner |
| field | ForeignKey → FieldData | No | NULL | Associated field |
| date | DateField | Yes | — | Activity date (indexed) |
| activity | CharField(20) | Yes | — | One of: watering, fertilizer, sowing, pesticide, harvest, other |
| details | TextField | Yes | — | Activity description |
| created_at | DateTimeField | Auto | now | Creation timestamp |
| updated_at | DateTimeField | Auto | now | Last edit timestamp |

**Indexes:** `(user, field, -date)`, `(date)` standalone

**Ordering:** `-date`, `-created_at`

---

### 4.5 FieldAlert (`field.FieldAlert`)

**Table:** `field_fieldalert`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Alert recipient |
| field | ForeignKey → FieldData | No | NULL | Associated field |
| log | ForeignKey → FieldLog | No | NULL | Associated log entry (if triggered by a log) |
| date | DateField | Yes | — | Alert date |
| message | CharField(255) | Yes | — | Alert message text |
| is_read | BooleanField | Yes | False | Read/unread status |
| created_at | DateTimeField | Auto | now | Creation timestamp |

**Indexes:** `(user, is_read, -date)`

---

### 4.6 IrrigationLog (`field.IrrigationLog`)

**Table:** `field_irrigationlog`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Log owner |
| field | ForeignKey → FieldData | Yes | — | Irrigated field |
| date | DateField | Yes | — | Irrigation date |
| water_amount | Decimal(8,2) | No | NULL | Water used (liters or mm) |
| duration_minutes | PositiveInteger | No | NULL | Duration in minutes |
| source | CharField(20) | No | "other" | One of: canal, borewell, rain, drip, sprinkler, other |
| notes | TextField | No | "" | Additional notes |
| created_at | DateTimeField | Auto | now | Creation timestamp |

---

### 4.7 CropHealthScan (`field.CropHealthScan`)

**Table:** `field_crophealthscan`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUIDField (PK) | Auto | uuid4 | Primary key |
| user | ForeignKey → User | Yes | — | Scanner |
| field | ForeignKey → FieldData | Yes | — | Scanned field |
| image_path | ImageField | Yes | — | Scan image (upload_to="ml_scans/") |
| detected_disease | CharField(100) | No | NULL | ML-detected disease name |
| confidence_score | FloatField | No | NULL | Detection confidence (0.0–1.0) |
| recommendation | TextField | No | NULL | Treatment recommendation |
| severity | CharField(20) | No | "LOW" | Severity level |
| scanned_at | DateTimeField | Auto | now | Scan timestamp |

---

### 4.8 Season (`finance.Season`)

**Table:** `finance_season`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| name | CharField(100) | Yes | — | Season name (e.g., "Kharif 2026") |
| season_type | CharField(20) | Yes | — | kharif, rabi, or zaid |
| year | IntegerField | Yes | — | Year |
| start_date | DateField | Yes | — | Season start |
| end_date | DateField | Yes | — | Season end |
| field | ForeignKey → FieldData | Yes | — | Associated field |
| crop | CharField(100) | No | "" | Crop grown this season |
| is_active | BooleanField | Yes | True | Active/inactive status |
| created_at | DateTimeField | Auto | now | Creation timestamp |

**Constraints:** Unique together: `(user, field, season_type, year)`

---

### 4.9 CostEntry (`finance.CostEntry`)

**Table:** `finance_costentry`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | Yes | — | Cost field |
| season | ForeignKey → Season | No | NULL | Associated season |
| category | CharField(20) | Yes | — | seeds, fertilizer, pesticide, labor, irrigation, equipment, transport, other |
| description | CharField(255) | Yes | — | Cost description |
| amount | Decimal(12,2) | Yes | — | Amount in ₹ |
| quantity | Decimal(10,2) | No | NULL | Quantity used |
| unit | CharField(50) | No | "" | Unit (kg, liters, hours) |
| date | DateField | Yes | — | Expense date |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

**Indexes:** `(user, field, -date)`, `(user, season, category)`

---

### 4.10 Revenue (`finance.Revenue`)

**Table:** `finance_revenue`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | Yes | — | Revenue field |
| season | ForeignKey → Season | No | NULL | Associated season |
| crop | CharField(100) | Yes | — | Crop sold |
| quantity_sold | Decimal(10,2) | Yes | — | Quantity sold |
| unit | CharField(50) | No | "kg" | Unit of sale |
| price_per_unit | Decimal(10,2) | Yes | — | Price per unit in ₹ |
| total_amount | Decimal(12,2) | Yes | — | Auto-calculated: quantity × price |
| buyer | CharField(255) | No | "" | Buyer name / Mandi |
| date | DateField | Yes | — | Sale date |
| notes | TextField | No | "" | Notes |
| created_at | DateTimeField | Auto | now | |

**Business Rule:** `total_amount` is auto-recalculated on every `save()` from `quantity_sold × price_per_unit`.

---

### 4.11 GovernmentScheme (`finance.GovernmentScheme`)

**Table:** `finance_governmentscheme`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| name | CharField(255) | Yes | — | Scheme name |
| scheme_type | CharField(20) | Yes | — | subsidy, loan, insurance, grant, training |
| description | TextField | Yes | — | Full description |
| benefits | TextField | No | "" | Benefits details |
| eligible_crops | JSONField | No | [] | List of eligible crop names |
| eligible_states | JSONField | No | [] | List of eligible Indian states |
| min_land_acres | Decimal(6,2) | No | 0 | Minimum land requirement |
| max_land_acres | Decimal(8,2) | No | NULL | Maximum land limit |
| max_subsidy_amount | Decimal(12,2) | No | NULL | Maximum subsidy in ₹ |
| subsidy_percentage | IntegerField | No | NULL | Subsidy percentage (0–100) |
| application_deadline | DateField | No | NULL | Deadline date |
| valid_from | DateField | No | NULL | Validity start |
| valid_until | DateField | No | NULL | Validity end |
| link | URLField | No | "" | Application/info URL |
| documents_required | JSONField | No | [] | List of required document names |
| is_active | BooleanField | Yes | True | Active flag |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

**Note:** This is an admin-managed reference table. Farmers have read-only access with eligibility-based filtering.

---

### 4.12 InsuranceClaim (`finance.InsuranceClaim`)

**Table:** `finance_insuranceclaim`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Claimant |
| field | ForeignKey → FieldData | Yes | — | Affected field |
| season | ForeignKey → Season | No | NULL | Season context |
| policy_number | CharField(50) | No | "" | Insurance policy number |
| crop | CharField(100) | Yes | — | Damaged crop name |
| area_affected_acres | Decimal(8,2) | Yes | — | Area affected |
| damage_type | CharField(20) | Yes | — | flood, drought, pest, disease, hail, fire, other |
| damage_date | DateField | Yes | — | Date of damage |
| damage_description | TextField | Yes | — | Description of damage |
| estimated_loss | Decimal(12,2) | Yes | — | Estimated loss in ₹ |
| claim_amount | Decimal(12,2) | No | NULL | Claim amount in ₹ |
| status | CharField(20) | Yes | "draft" | draft → submitted → under_review → approved/rejected → paid |
| submitted_at | DateTimeField | No | NULL | Submission timestamp |
| reviewed_at | DateTimeField | No | NULL | Review timestamp |
| reviewer_notes | TextField | No | "" | Admin review notes |
| bank_account | EncryptedCharField(200) | No | "" | Encrypted bank account number |
| ifsc_code | EncryptedCharField(200) | No | "" | Encrypted IFSC code |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

**Security:** `bank_account` and `ifsc_code` use Fernet symmetric encryption at rest.

---

### 4.13 FinanceTransaction (`finance.FinanceTransaction`)

**Table:** `finance_financetransaction`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUIDField (PK) | Auto | uuid4 | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | No | NULL | Associated field |
| type | CharField(10) | Yes | — | EXPENSE or INCOME |
| category | CharField(100) | Yes | — | Free-text category |
| amount | Decimal(12,2) | Yes | — | Amount in ₹ |
| date | DateField | Yes | — | Transaction date (indexed) |
| notes | TextField | No | NULL | Notes |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

**Indexes:** `(user, type)`, `(user, date)`

---

### 4.14 SeasonCalendar (`planning.SeasonCalendar`)

**Table:** `planning_seasoncalendar`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | Yes | — | Subject field |
| title | CharField(255) | Yes | — | Event title |
| activity_type | CharField(20) | Yes | — | sowing, irrigation, fertilizing, spraying, weeding, harvesting, other |
| description | TextField | No | "" | Event description |
| start_date | DateField | Yes | — | Start date |
| end_date | DateField | Yes | — | End date |
| status | CharField(20) | No | "planned" | planned, in_progress, completed, cancelled |
| notes | TextField | No | "" | Notes |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

---

### 4.15 InventoryItem (`planning.InventoryItem`)

**Table:** `planning_inventoryitem`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| name | CharField(255) | Yes | — | Item name |
| category | CharField(20) | Yes | — | seeds, fertilizer, pesticide, herbicide, tools, other |
| description | TextField | No | "" | Item description |
| quantity | Decimal(10,2) | No | 0 | Current stock quantity |
| unit | CharField(50) | Yes | — | Unit (kg, liters, packets) |
| reorder_level | Decimal(10,2) | No | 0 | Low stock threshold |
| purchase_price | Decimal(10,2) | No | NULL | Unit purchase price in ₹ |
| supplier | CharField(255) | No | "" | Supplier name |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

**Constraints:** `CHECK (quantity >= 0)` — inventory quantity cannot go negative.

**Computed Property:** `is_low_stock` → `True` if `quantity <= reorder_level`

---

### 4.16 InventoryTransaction (`planning.InventoryTransaction`)

**Table:** `planning_inventorytransaction`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| item | ForeignKey → InventoryItem | Yes | — | Subject item |
| field | ForeignKey → FieldData | No | NULL | Field this transaction was for |
| transaction_type | CharField(20) | Yes | — | purchase, use, adjustment, return |
| quantity | Decimal(10,2) | Yes | — | Transaction quantity |
| date | DateField | Yes | — | Transaction date |
| notes | TextField | No | "" | Notes |
| created_at | DateTimeField | Auto | now | |

**Business Logic on `save()`:**
- `purchase` or `return` → item quantity increases by transaction quantity (atomic F() update)
- `use` → item quantity decreases; raises `ValidationError` if insufficient stock
- `adjustment` → no automatic quantity change

---

### 4.17 LaborEntry (`planning.LaborEntry`)

**Table:** `planning_laborentry`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | Yes | — | Work field |
| worker_name | CharField(255) | Yes | — | Worker's name |
| work_type | CharField(100) | Yes | — | Type of work (sowing, weeding, harvesting, etc.) |
| hours_worked | Decimal(5,2) | Yes | — | Hours worked |
| hourly_rate | Decimal(8,2) | Yes | — | Rate per hour in ₹ |
| total_wage | Decimal(10,2) | Yes | — | Auto-calculated: hours × rate |
| date | DateField | Yes | — | Work date |
| notes | TextField | No | "" | Notes |
| is_paid | BooleanField | No | False | Payment status |
| created_at | DateTimeField | Auto | now | |

**Business Rule:** `total_wage` is auto-recalculated on every `save()`.

---

### 4.18 Equipment (`planning.Equipment`)

**Table:** `planning_equipment`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| name | CharField(255) | Yes | — | Equipment name |
| equipment_type | CharField(100) | Yes | — | Type (Tractor, pump, sprayer, etc.) |
| description | TextField | No | "" | Description |
| purchase_date | DateField | No | NULL | Purchase date |
| purchase_price | Decimal(12,2) | No | NULL | Purchase price in ₹ |
| status | CharField(20) | No | "available" | available, in_use, maintenance, retired |
| last_maintenance | DateField | No | NULL | Last maintenance date |
| created_at | DateTimeField | Auto | now | |

---

### 4.19 EquipmentBooking (`planning.EquipmentBooking`)

**Table:** `planning_equipmentbooking`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| equipment | ForeignKey → Equipment | Yes | — | Booked equipment |
| field | ForeignKey → FieldData | Yes | — | Usage field |
| start_datetime | DateTimeField | Yes | — | Booking start |
| end_datetime | DateTimeField | Yes | — | Booking end |
| purpose | CharField(255) | Yes | — | Usage purpose |
| notes | TextField | No | "" | Notes |
| is_completed | BooleanField | No | False | Completion status |
| created_at | DateTimeField | Auto | now | |

**Constraints:**
- `CHECK (end_datetime > start_datetime)`
- `clean()` validates no overlapping bookings for the same equipment (active bookings only)

---

### 4.20 Plan (`planning.Plan`)

**Table:** `planning_plan`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | UUIDField (PK) | Auto | uuid4 | Primary key |
| user | ForeignKey → User | Yes | — | Owner |
| field | ForeignKey → FieldData | Yes | — | Plan field |
| crop_type | CharField(100) | Yes | — | Crop to be grown |
| start_date | DateField | Yes | — | Planned start date |
| estimated_harvest_date | DateField | Yes | — | Estimated harvest date |
| status | CharField(20) | No | "PLANNED" | PLANNED, ACTIVE, COMPLETED, FAILED |
| risk_score | FloatField | No | NULL | LSTM-predicted risk score |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

---

### 4.21 ChatSession (`chat.ChatSession`)

**Table:** `chat_chatsession`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| user | ForeignKey → User | No | NULL | Session owner (nullable for legacy) |
| session_id | CharField(255) | Yes | — | Unique session identifier (indexed) |
| created_at | DateTimeField | Auto | now | |
| updated_at | DateTimeField | Auto | now | |

---

### 4.22 ChatMessage (`chat.ChatMessage`)

**Table:** `chat_chatmessage`

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| id | AutoField (PK) | Auto | — | Primary key |
| session | ForeignKey → ChatSession | Yes | — | Parent session |
| role | CharField(10) | Yes | — | "user" or "model" |
| text | TextField(10000) | Yes | — | Message content (max 10k chars) |
| timestamp | DateTimeField | Auto | now | |

**Indexes:** `(session, -timestamp)`

---

## 5. FEATURE SPECIFICATIONS

### Feature: User Registration
**Priority:** 🔴 P0  
**User Roles:** Guest  
**Description:** Self-service account creation with username, email, and password.

#### User Flow
1. User navigates to `/signup`
2. User sees a registration form with fields: Username, Email, Password, Confirm Password
3. User fills in all fields and clicks "Create Account"
4. System validates inputs (username uniqueness, email format, password strength via Django validators)
5. On success: If `REQUIRE_EMAIL_VERIFICATION=True`, system sends verification email and shows "Check your email" message. If False, system auto-creates Knox token, stores in localStorage, and redirects to `/dashboard`
6. On error: System displays specific field-level errors (e.g., "Username already taken")

#### Business Logic
- Username: required, max 150 chars, unique
- Email: required, valid format
- Password: validated by Django's built-in validators (min 8 chars, not too common, not entirely numeric, not too similar to username)
- If email verification is enabled, user.is_active is set to False until verified

#### API Requirements
- **Endpoint:** `POST /signup`
- **Request Body:** `{ "username": string, "email": string, "password": string }`
- **Success Response (201):** `{ "token": string, "expiry": string, "user": { "id": int, "username": string, "email": string } }`
- **Success Response (201, verification required):** `{ "message": "...", "email_verification_required": true }`
- **Error Response (400):** `{ "username": ["This field must be unique."] }` (or other field errors)

#### Acceptance Criteria
- [ ] User can register with valid username/email/password
- [ ] Duplicate username returns 400 with clear error
- [ ] Weak password returns validation errors
- [ ] After registration (no verification), user is immediately authenticated and redirected to dashboard
- [ ] With email verification enabled, user receives email with verification link

---

### Feature: User Login
**Priority:** 🔴 P0  
**User Roles:** Guest  
**Description:** Username/password authentication returning a Knox token.

#### User Flow
1. User navigates to `/login`
2. User enters username and password
3. User clicks "Login"
4. System authenticates via Django's `authenticate()` (constant-time comparison)
5. On success: Knox token created, stored in `localStorage.authToken`, user JSON stored in `localStorage.authUser`, redirect to `/dashboard`
6. On error: Display "Invalid credentials" (no username/password enumeration)

#### Business Logic
- Rate limited: 5 attempts per minute per IP (LoginRateThrottle)
- Disabled accounts return "Account is disabled. Contact support." (403)
- On successful login, a 30-minute inactivity timer starts. Mouse/keyboard/scroll activity resets the timer (throttled to 30s intervals). On expiry, automatic logout + toast notification.

#### API Requirements
- **Endpoint:** `POST /login`
- **Request Body:** `{ "username": string, "password": string }`
- **Success Response (200):** `{ "token": string, "expiry": string, "user": { "id": int, "username": string, "email": string } }`
- **Error Response (401):** `{ "error": "Invalid credentials" }`
- **Error Response (429):** Rate limit exceeded

#### Acceptance Criteria
- [ ] Valid credentials return token and user data
- [ ] Invalid credentials return 401 without leaking which field was wrong
- [ ] After 5 failed attempts in 1 minute, returns 429
- [ ] Token is stored in localStorage and used for subsequent API calls
- [ ] 30-minute inactivity timer triggers automatic logout

---

### Feature: Field Management (CRUD)
**Priority:** 🔴 P0  
**User Roles:** Farmer  
**Description:** Create, list, view, and delete agricultural fields with GeoJSON polygon boundaries drawn on an interactive Leaflet map.

#### User Flow
1. User navigates to "My Field" tab in dashboard
2. User sees a list of existing fields (name, crop type, created date) and a Leaflet map displaying all field polygons
3. To add a field: User clicks "Add Field" → draws a polygon on the map by clicking vertices → enters field name and crop type → clicks "Save"
4. System validates the polygon (≥3 points, valid coordinates) and creates the field
5. Field appears in the list; map zooms to show all fields
6. To delete: User clicks delete icon on a field → confirmation dialog → field removed

#### Business Logic
- GET `/field/data` returns all fields for the authenticated user
- POST `/field/data` creates a new field (user auto-set from token)
- DELETE `/field/data/<id>` deletes a specific field (ownership verified)
- Polygon validation: must be valid GeoJSON with ≥3 coordinate points, each point [lng, lat] with lng ∈ [-180, 180] and lat ∈ [-90, 90]
- When a field is deleted, CASCADE removes all associated logs, alerts, irrigation logs, health scans, costs, revenues, seasons, calendar events, etc.

#### UI/UX Requirements
- **Map:** Full-height Leaflet map with satellite tile layer, polygon drawing tools (Leaflet Draw), geocoder search bar (leaflet-geosearch)
- **Field List:** Card layout showing field name, crop type, area (calculated via Turf.js), and creation date
- **Empty State:** "No fields yet. Draw a polygon on the map to add your first field."
- **Loading State:** Skeleton cards + map placeholder
- **Error State:** Toast notification with error message

#### Acceptance Criteria
- [ ] User can draw a polygon on the map and save it as a field
- [ ] Field list updates immediately after creation
- [ ] User can delete a field with confirmation dialog
- [ ] Invalid polygons (< 3 points) are rejected with error message
- [ ] Fields are user-scoped — user A cannot see user B's fields
- [ ] Map displays all user fields with colored polygons

---

### Feature: Satellite Data Analysis (Earth Engine)
**Priority:** 🔴 P0  
**User Roles:** Farmer  
**Description:** Retrieve and display satellite-derived vegetation indices (NDVI, EVI, SAVI), water index (NDWI), soil moisture, temperature, and rainfall for a user's field via Google Earth Engine.

#### User Flow
1. User navigates to "Field Report" or "Analytics" tab
2. System fetches EE data for the selected field via `GET /field/ee?field_id=N`
3. User sees: current index values (gauge/number displays), time series charts (NDVI, NDWI over past months), color-coded health indicators
4. User can switch between fields using a dropdown selector

#### Business Logic
- `fetchEEData()` in `field/utils.py` calls Earth Engine API:
  - Computes median NDVI, EVI, SAVI from Sentinel-2 over the last 30 days within the field polygon
  - Computes NDWI time series from Sentinel-2 (90-day window)
  - Retrieves MODIS-based temperature and ERA5 rainfall
  - Retrieves soil moisture from SMAP/FLDAS
- Results are returned as JSON with current values and time series arrays
- If EE is unavailable, returns `{"error": "...", "details": "..."}` with 503 status
- Rate limited: 20 requests/hour per user (EarthEngineThrottle)

#### API Requirements
- **Endpoint:** `GET /field/ee`
- **Query Params:** `field_id` (optional, defaults to user's first field)
- **Response (200):**
```json
{
  "NDVI": 0.72,
  "EVI": 0.45,
  "SAVI": 0.55,
  "crop_type_class": 1.0,
  "rainfall_mm": 12.5,
  "temperature_K": 305.2,
  "soil_moisture": 0.35,
  "ndvi_time_series": [{"date": "2026-03-01", "NDVI": 0.65}, ...],
  "ndwi_time_series": [{"date": "2026-03-01", "NDWI": 0.12}, ...]
}
```
- **Error Response (503):** `{"error": "Earth Engine unavailable", "details": "..."}`

#### Acceptance Criteria
- [ ] EE data loads within 15 seconds for a typical field
- [ ] NDVI, EVI, SAVI displayed as gauges/numbers with color coding (red < 0.3, yellow 0.3–0.5, green > 0.5)
- [ ] Time series charts display correctly with date axis
- [ ] Graceful fallback when EE is unavailable (error toast, empty state)

---

### Feature: Pest/Disease Detection (CNN)
**Priority:** 🔴 P0  
**User Roles:** Farmer  
**Description:** Upload a photo of a crop leaf; the system validates it's a plant image using Gemini Vision, then runs a MobileNetV2 CNN to classify it among 38 possible crop disease classes.

#### User Flow
1. User navigates to "Pest Detection" tab
2. User clicks "Upload Image" or takes a photo with camera
3. System validates: file size ≤ 10MB, type is JPEG or PNG
4. System saves image, then calls Gemini Vision to verify it shows a plant/crop
5. If NOT a plant image: image is deleted, error shown with "This doesn't appear to be a plant or crop image"
6. If valid plant: CNN model runs inference, returns disease name + confidence + treatment recommendations
7. Results displayed with disease name, confidence bar, severity indicator, and recommended actions
8. Historical scan results listed below

#### Business Logic
- CNN model: MobileNetV2 fine-tuned on PlantVillage dataset (38 classes covering 14 crops)
- Input preprocessing: resize to 224×224, normalize with ImageNet mean/std
- Output: predicted class label, confidence score, top-3 predictions
- Image validation via Gemini 2.0 Flash vision model (fail-open: if Gemini fails, image proceeds to CNN)
- Rate limited: 30 req/hour (MLInferenceThrottle)

#### API Requirements
- **Endpoint:** `POST /field/pest/report`
- **Content-Type:** `multipart/form-data`
- **Request Body:** `image` (file field)
- **Success Response (201):**
```json
{
  "predicted_class": "Tomato___Late_blight",
  "confidence": 0.94,
  "top3": [
    {"class": "Tomato___Late_blight", "confidence": 0.94},
    {"class": "Tomato___Early_blight", "confidence": 0.04},
    {"class": "Tomato___Septoria_leaf_spot", "confidence": 0.01}
  ],
  "upload_id": 42,
  "uploaded_at": "2026-04-11T10:00:00Z",
  "image_validated": true,
  "validation_confidence": "high"
}
```
- **Error (400, not plant):** `{"error": "Invalid image", "message": "This doesn't appear to be...", "is_plant": false}`

---

### Feature: Health Score
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** Multi-factor crop health score fusing satellite indices, CNN disease detection, and LSTM risk prediction into a 0–100 score.

#### Business Logic
The `get_health_score()` function in `ml_engine/health_score.py` fuses three signals:
1. **NDVI Score (weight: 0.40):** Maps latest NDVI value to 0–100 using a sigmoid-like curve
2. **CNN Score (weight: 0.35):** If a pest image is available, runs disease detection. "Healthy" → high score, disease detected → score reduced proportional to confidence
3. **LSTM Risk Score (weight: 0.25):** Runs risk prediction from time series. Low risk → high health, high risk → low health

Final score = weighted sum, clamped to [0, 100]. Rating bands: Excellent (≥80), Good (60–79), Fair (40–59), Poor (20–39), Critical (<20).

#### API Requirements
- **Endpoint:** `GET /field/healthscore`
- **Query Params:** `field_id` (optional)
- **Response:**
```json
{
  "score": 78,
  "rating": "Good",
  "components": {
    "ndvi_score": 85,
    "cnn_score": 70,
    "lstm_score": 75
  },
  "ndvi_latest": 0.72,
  "disease_detected": "None",
  "risk_level": "Low"
}
```

---

### Feature: AI Chatbot
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** A floating chatbot widget powered by Gemini 2.5 Flash, specialized in agriculture topics. Supports conversation history, session management, and voice input.

#### User Flow
1. User clicks the floating chat bubble (bottom-right corner of dashboard)
2. Chat panel slides up with message history (if existing session)
3. User types a question or uses voice recording (MediaRecorder API)
4. System sends question + last 20 messages of history to Gemini
5. Gemini responds with agricultural advice
6. Both user message and model reply are persisted to DB
7. User can clear history or start a new session

#### Business Logic
- System instruction defines Gemini as an agricultural assistant
- Language: responds in the user's language
- Non-agriculture topics: politely redirected
- Context window: last 20 messages
- Session limit: 50 sessions per user (oldest auto-deleted when exceeded)
- Question length: max 4000 characters
- Rate limited: 60 req/hour (GeminiChatThrottle)
- IDOR prevention: session ownership verified on every request

#### API Requirements
- **Endpoint:** `POST /api/chat`
- **Request:** `{ "question": string, "sessionId": string|null, "clearHistory": boolean }`
- **Response:** `{ "reply": string, "sessionId": string, "conversationLength": int }`
- **Error (503):** `{"error": "Chat service not configured"}` (no API key)
- **Error (502):** `{"error": "Chat service temporarily unavailable"}` (Gemini error)

---

### Feature: Weather Integration
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** Real-time weather data for the user's field location, displayed as a widget on the dashboard with current conditions and multi-day forecast.

#### Business Logic
- Backend proxies OpenWeatherMap API using the polygon centroid as coordinates
- `GET /field/coord` returns centroid lat/lng for the user's field
- Frontend `useWeather` hook fetches coordinates, then calls OpenWeatherMap directly for current weather + forecast
- Temperature displayed in °C, wind in km/h, humidity as percentage
- Weather icons from OpenWeatherMap CDN

---

### Feature: Cost & Revenue Tracking
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** Full CRUD for farm expense entries (categorized: seeds, fertilizer, pesticide, labor, irrigation, equipment, transport, other) and revenue entries (crop sales with quantity, price per unit, auto-calculated total).

#### Business Logic
- Costs grouped by category with summary view
- Revenue auto-calculates total = quantity × price
- Filter by field, season, date range
- Cost summary endpoint aggregates totals by category

---

### Feature: P&L Dashboard
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** Profit & Loss overview showing total costs, total revenue, net profit/loss, and category breakdowns with charts.

#### API Requirements
- **Endpoint:** `GET /finance/pnl`
- **Query Params:** `field_id`, `season_id`, `start_date`, `end_date`
- **Response:** Total costs, total revenue, net P&L, cost breakdown by category, revenue breakdown by crop

---

### Feature: Market Prices
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Live agricultural commodity prices from Indian mandis (markets), fetched from data.gov.in / Agmarknet API.

#### API Requirements
- **Endpoint:** `GET /finance/market-prices`
- **Query Params:** `state` (required), `commodity`, `market`
- **Response:** List of `{ commodity, market, state, min_price, max_price, modal_price, date }`

---

### Feature: Price Forecast
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** LSTM-based price prediction showing estimated future prices for selected commodities with trend charts.

---

### Feature: Government Scheme Matcher
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Discover government subsidies, loans, insurance, and grant programs with eligibility filtering based on crop type, state, and land size.

---

### Feature: Insurance Claims
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** PMFBY (Pradhan Mantri Fasal Bima Yojana) insurance claim creation and status tracking with encrypted bank account storage.

#### Business Logic
- Status workflow: draft → submitted → under_review → approved/rejected → paid
- Bank account and IFSC code encrypted at rest using Fernet
- Only the claim owner can view their claims

---

### Feature: Irrigation Scheduling & Logging
**Priority:** 🟠 P1  
**User Roles:** Farmer  
**Description:** AI-generated irrigation schedules based on crop type, soil moisture, and weather data, plus manual irrigation event logging.

---

### Feature: Yield Prediction
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Statistical yield estimation based on crop type, region, field area, and satellite-derived health indices.

---

### Feature: Crop Rotation Planning
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Rule-based crop rotation recommendations with agronomic compatibility checks (nitrogen fixers, heavy feeders, etc.).

---

### Feature: Season Calendar
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Calendar view for planning farm activities (sowing, irrigation, fertilizing, spraying, weeding, harvesting) with status tracking.

---

### Feature: Inventory Tracker
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Track farm inputs (seeds, fertilizers, pesticides, tools) with stock levels, reorder alerts, and transaction history (purchase, use, return, adjustment).

#### Business Logic
- Stock quantity updated atomically via Django F() expressions to prevent race conditions
- Use transactions validate sufficient stock before deduction
- Low stock flag: `quantity <= reorder_level`

---

### Feature: Labor Management
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Track farm workers, hours worked, hourly rates, total wages, and payment status.

#### Business Logic
- `total_wage` auto-calculated as `hours_worked × hourly_rate` on every save

---

### Feature: Equipment Scheduler
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Equipment registry with booking/scheduling system that prevents double-booking via overlap validation.

#### Business Logic
- `clean()` method checks for overlapping bookings on the same equipment
- Overlapping = existing booking where `start < new.end AND end > new.start`

---

### Feature: AWD Irrigation Detection
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Analyze NDWI time series from satellite data to detect Alternate Wetting and Drying (AWD) irrigation practices.

---

### Feature: Carbon Credit Estimation
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Estimate carbon emission reductions from AWD practices, calculated per hectare based on area and NDWI patterns.

---

### Feature: Soil Advice
**Priority:** 🟡 P2  
**User Roles:** Farmer  
**Description:** Gemini AI-generated soil health advice based on satellite-derived soil moisture, NDVI, and crop type.

---

### Feature: PDF/Excel Report Export
**Priority:** 🟢 P3  
**User Roles:** Farmer  
**Description:** Export field reports, P&L dashboards, and analytics as downloadable PDF files using jsPDF with auto-table support.

---

### Feature: Dark/Light Theme
**Priority:** 🟢 P3  
**User Roles:** All  
**Description:** Theme toggle between dark and light modes, persisted in localStorage via `next-themes` ThemeProvider.

---

### Feature: Voice Input for Chat
**Priority:** 🟢 P3  
**User Roles:** Farmer  
**Description:** Record voice messages via MediaRecorder API, converted to text for chatbot input.

---

## 6. API REFERENCE

### Authentication
All authenticated endpoints require `Authorization: Token <knox_token>` header.

### Complete Endpoint List

| Method | Path | Auth | Rate Limit | Description |
|--------|------|------|-----------|-------------|
| POST | `/login` | No | 5/min (anon) | User login |
| POST | `/signup` | No | 5/min (anon) | User registration |
| GET | `/test_token` | Yes | — | Validate current token |
| POST | `/logout` | Yes | — | Invalidate current token |
| POST | `/password-reset` | No | 3/hour | Request password reset email |
| POST | `/password-reset-confirm` | No | 3/hour | Set new password with token |
| POST | `/verify-email` | No | — | Verify email from link |
| POST | `/resend-verification` | No | 5/min | Resend verification email |
| **Field CRUD** |||||
| GET | `/field/data` | Yes | 60/min | List user's fields |
| POST | `/field/data` | Yes | 60/min | Create a new field |
| DELETE | `/field/data/<id>` | Yes | 60/min | Delete a field |
| GET | `/field/coord` | Yes | 60/min | Get field centroid coordinates |
| POST | `/field/set_polygon` | Yes | 60/min | Update field polygon |
| **Field Analysis** |||||
| GET | `/field/ee` | Yes | 20/hour | Earth Engine satellite analysis |
| GET | `/field/awd` | Yes | 20/hour | AWD detection from NDWI |
| GET | `/field/cc` | Yes | 20/hour | Carbon credit estimation |
| GET | `/field/pestpredict` | Yes | 30/hour | LSTM pest/risk prediction |
| GET | `/field/healthscore` | Yes | 30/hour | Multi-factor health score |
| POST | `/field/pest/report` | Yes | 30/hour | Upload image for CNN pest detection |
| GET | `/field/pest/report` | Yes | 60/min | List historical pest scans |
| GET | `/field/diagnose` | Yes | 30/hour | Diagnose crop health |
| GET | `/field/weather` | Yes | 60/min | Weather data for field |
| GET | `/field/soil-advice` | Yes | 30/hour | Gemini-powered soil advice |
| GET | `/field/yield-prediction` | Yes | 30/hour | Yield estimate |
| **Field Logs & Alerts** |||||
| GET | `/field/logs` | Yes | 60/min | List field logs |
| POST | `/field/logs` | Yes | 60/min | Create field log |
| PUT | `/field/logs/<id>` | Yes | 60/min | Update field log |
| DELETE | `/field/logs/<id>` | Yes | 60/min | Delete field log |
| GET | `/field/alerts` | Yes | 60/min | List field alerts |
| PATCH | `/field/alerts/<id>` | Yes | 60/min | Mark alert as read |
| POST | `/field/alerts/mark-all-read` | Yes | 60/min | Bulk mark all alerts read |
| **Irrigation** |||||
| GET | `/field/irrigation-schedule` | Yes | 60/min | Get AI irrigation schedule |
| GET | `/field/irrigation-logs` | Yes | 60/min | List irrigation logs |
| POST | `/field/irrigation-logs` | Yes | 60/min | Create irrigation log |
| DELETE | `/field/irrigation-logs/<id>` | Yes | 60/min | Delete irrigation log |
| **Finance** |||||
| GET | `/finance/costs` | Yes | 60/min | List cost entries |
| POST | `/finance/costs` | Yes | 60/min | Create cost entry |
| PUT | `/finance/costs/<id>` | Yes | 60/min | Update cost entry |
| DELETE | `/finance/costs/<id>` | Yes | 60/min | Delete cost entry |
| GET | `/finance/costs/summary` | Yes | 60/min | Cost summary by category |
| GET | `/finance/revenue` | Yes | 60/min | List revenue entries |
| POST | `/finance/revenue` | Yes | 60/min | Create revenue entry |
| DELETE | `/finance/revenue/<id>` | Yes | 60/min | Delete revenue entry |
| GET | `/finance/seasons` | Yes | 60/min | List seasons |
| POST | `/finance/seasons` | Yes | 60/min | Create season |
| DELETE | `/finance/seasons/<id>` | Yes | 60/min | Delete season |
| GET | `/finance/pnl` | Yes | 60/min | P&L dashboard data |
| GET | `/finance/market-prices` | Yes | 60/min | Market prices |
| GET | `/finance/price-forecast` | Yes | 30/hour | Price forecast |
| GET | `/finance/schemes` | Yes | 60/min | List government schemes |
| GET | `/finance/schemes/<id>` | Yes | 60/min | Scheme detail |
| GET | `/finance/insurance` | Yes | 60/min | List insurance claims |
| POST | `/finance/insurance` | Yes | 60/min | Create insurance claim |
| GET | `/finance/insurance/<id>` | Yes | 60/min | Claim detail |
| PUT | `/finance/insurance/<id>` | Yes | 60/min | Update claim |
| **Planning** |||||
| GET | `/planning/calendar` | Yes | 60/min | List calendar events |
| POST | `/planning/calendar` | Yes | 60/min | Create calendar event |
| PUT | `/planning/calendar/<id>` | Yes | 60/min | Update calendar event |
| DELETE | `/planning/calendar/<id>` | Yes | 60/min | Delete calendar event |
| GET | `/planning/inventory` | Yes | 60/min | List inventory items |
| POST | `/planning/inventory` | Yes | 60/min | Create inventory item |
| PUT | `/planning/inventory/<id>` | Yes | 60/min | Update inventory item |
| DELETE | `/planning/inventory/<id>` | Yes | 60/min | Delete inventory item |
| POST | `/planning/inventory/<id>/transaction` | Yes | 60/min | Record inventory transaction |
| GET | `/planning/transactions` | Yes | 60/min | List all transactions |
| GET | `/planning/labor` | Yes | 60/min | List labor entries |
| POST | `/planning/labor` | Yes | 60/min | Create labor entry |
| DELETE | `/planning/labor/<id>` | Yes | 60/min | Delete labor entry |
| GET | `/planning/equipment` | Yes | 60/min | List equipment |
| POST | `/planning/equipment` | Yes | 60/min | Create equipment |
| PUT | `/planning/equipment/<id>` | Yes | 60/min | Update equipment |
| DELETE | `/planning/equipment/<id>` | Yes | 60/min | Delete equipment |
| POST | `/planning/equipment/<id>/book` | Yes | 60/min | Book equipment |
| GET | `/planning/bookings` | Yes | 60/min | List bookings |
| DELETE | `/planning/bookings/<id>` | Yes | 60/min | Cancel booking |
| GET | `/planning/rotation` | Yes | 60/min | Crop rotation recommendations |
| **Chat** |||||
| POST | `/api/chat` | Yes | 60/hour | Send message to AI chatbot |
| GET | `/api/chat/history/<session_id>` | Yes | 60/min | Get chat history |
| DELETE | `/api/chat/history/<session_id>` | Yes | 60/min | Delete chat session |
| **Finance Transactions** |||||
| GET | `/finance/transactions` | Yes | 60/min | List finance ledger |
| POST | `/finance/transactions` | Yes | 60/min | Create transaction |
| GET | `/finance/transactions/<id>` | Yes | 60/min | Transaction detail |
| **Plans** |||||
| GET | `/planning/plans` | Yes | 60/min | List crop plans |
| POST | `/planning/plans` | Yes | 60/min | Create crop plan |
| GET | `/planning/plans/<id>` | Yes | 60/min | Plan detail |
| **Health & Monitoring** |||||
| GET | `/health` | No | — | Liveness check |
| GET | `/ready` | No | — | Readiness check (DB, ML, EE) |
| GET | `/metrics` | Admin only | — | Application metrics |
| GET | `/api/schema/` | No | — | OpenAPI 3.0 schema |
| GET | `/api/docs/` | No | — | Swagger UI |
| GET | `/api/redoc/` | No | — | ReDoc documentation |

---

## 7. AUTHENTICATION & AUTHORIZATION

### Auth Flow

**Registration:** `POST /signup` → validates → creates User → creates Knox AuthToken → returns token + user JSON

**Login:** `POST /login` → `authenticate()` → creates Knox AuthToken → returns token + user JSON + expiry

**Token Strategy:**
- Knox token-based authentication (not JWT)
- Each login creates a new token (token per device/session)
- Token stored in frontend `localStorage` as `authToken`
- Token sent in every request as `Authorization: Token <token>`
- Token has configurable TTL (default: Session-based per Knox settings)
- Frontend implements 30-minute inactivity auto-logout (client-side timer)

**Token Validation on Page Load:**
- On mount, `AuthContext` checks `localStorage` for stored token
- Validates by calling `GET /test_token` with the stored token
- If valid: hydrates auth state; if invalid: clears storage, shows login

**Logout:** 
- Frontend calls `POST /logout` (best-effort, raw fetch to avoid 401 loop)
- Backend deletes the Knox token from DB (`request._auth.delete()`)
- Frontend clears `localStorage` (authToken, authUser), resets state

**Password Reset:**
1. `POST /password-reset` with email → sends reset link via email (SMTP)
2. User clicks link with `uidb64` and `token` parameters
3. `POST /password-reset-confirm` with `uidb64`, `token`, new `password`
4. Password updated, Django password validators enforced

**401 Handling:**
- `api.ts` has a global 401 interceptor (`fireUnauthorized`)
- Debounced: only fires once per 2-second window (prevents cascade from parallel requests)
- `AuthContext.logout()` has re-entrancy guard (`isLoggingOutRef`) to prevent recursive logout loops
- Local state cleared FIRST, then best-effort server logout via raw `fetch()`

### Authorization Matrix

| Resource | Farmer (own data) | Farmer (other's data) | Admin | Guest |
|----------|:---:|:---:|:---:|:---:|
| Fields CRUD | ✅ | ❌ | ✅ | ❌ |
| Field Logs/Alerts | ✅ | ❌ | ✅ | ❌ |
| EE Analysis | ✅ | ❌ | ✅ | ❌ |
| Pest Detection | ✅ | ❌ | ✅ | ❌ |
| Health Score | ✅ | ❌ | ✅ | ❌ |
| Chat | ✅ | ❌ | ✅ | ❌ |
| Cost/Revenue | ✅ | ❌ | ✅ | ❌ |
| Govt Schemes (read) | ✅ | ✅ | ✅ | ❌ |
| Govt Schemes (write) | ❌ | ❌ | ✅ | ❌ |
| Insurance Claims | ✅ | ❌ | ✅ | ❌ |
| Inventory/Labor/Equipment | ✅ | ❌ | ✅ | ❌ |
| Metrics | ❌ | ❌ | ✅ | ❌ |
| Health/Ready checks | ✅ | ✅ | ✅ | ✅ |
| API Docs | ✅ | ✅ | ✅ | ✅ |

**Row-Level Security:** All views filter querysets by `request.user`. Example: `FieldData.objects.filter(user=request.user)`. This is enforced at the view layer consistently across all apps.

---

## 8. UI/UX SPECIFICATIONS

### 8.1 Design System

- **Color Palette:** TailwindCSS defaults + custom green-dominant theme. Primary: emerald/green tones. Semantic: red (destructive), yellow (warning), green (success), blue (info). Dark mode with gray-900 backgrounds.
- **Typography:** System font stack (TailwindCSS default sans). Sizes: text-xs through text-4xl. Font weights: normal (400), medium (500), semibold (600), bold (700).
- **Spacing:** 4px base unit (Tailwind's spacing scale). Common: p-2, p-4, p-6, p-8, gap-2, gap-4.
- **Breakpoints:** `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`, `2xl: 1536px`. Sidebar hidden on < lg, shown on ≥ lg.
- **Component Library:** shadcn/ui built on Radix UI primitives — 40+ components including Button, Card, Dialog, Select, Toast, Tabs, Tooltip, etc.
- **Icons:** Material Symbols (outline, variable fill) for navigation; Lucide React for inline icons.

### 8.2 Pages & Screens

#### Page: Landing Page (`/`)
**Access:** Public (Guest)  
**Purpose:** Marketing page introducing KrishiSaarthi with feature highlights and CTA to register/login.

Layout: Full-page with hero section, feature cards, testimonials, and footer. Animated elements via Framer Motion.

#### Page: Login (`/login`)
**Access:** Public  
**Purpose:** Authenticate existing users.

Components: Username input, password input (with show/hide toggle), "Login" button, "Forgot Password?" link, "Don't have an account? Sign up" link.

#### Page: Signup (`/signup`)
**Access:** Public  
**Purpose:** Register new users.

Components: Username, email, password, confirm password inputs. Password strength indicator. Terms acceptance.

#### Page: Dashboard (`/dashboard`)
**Access:** Authenticated (ProtectedRoute)  
**Purpose:** Main application shell with sidebar navigation and tab-based content rendering.

Layout:
- **Left Sidebar (264px, fixed on desktop):** Logo ("AgriSmart"), 20 navigation items grouped into: Core (Dashboard, My Field, Field Report, Analytics), Field Operations (Field Log, Pest Detection, Irrigation, Yield Prediction, Alerts), Planning (Season Calendar, Crop Rotation, Inventory, Labor, Equipment), Finance & Market (Costs & Revenue, Profit & Loss, Market Prices, Price Forecast, Govt Schemes, Insurance). User profile section at bottom with avatar, username, email, and Logout button.
- **Header (64px):** Mobile hamburger menu, page title, search bar (desktop), notification bell with unread count badge.
- **Main Content Area:** Scrollable content panel rendering the active tab's component.
- **Floating ChatBot:** Fixed position bottom-right corner.

### 8.3 Navigation Structure

```
/ (Landing - public)
/login (Login - public)
/signup (Signup - public)
/forgot-password (Password reset request - public)
/reset-password/:uid/:token (Password reset confirm - public)
/dashboard (Protected - all tabs rendered via hash routing)
  #home (HomeDashboard)
  #my-field (MyField + MapView)
  #field-report (FieldReport + EEData)
  #data-analytics (DataAnalytics)
  #field-log (FieldLog)
  #pest (Pest)
  #irrigation (IrrigationScheduler)
  #yield-prediction (YieldPrediction)
  #alerts (FieldAlerts)
  #season-calendar (SeasonCalendar)
  #rotation (RotationPlanner)
  #inventory (InventoryTracker)
  #labor (LaborManager)
  #equipment (EquipmentScheduler)
  #cost-calculator (CostCalculator)
  #pnl-dashboard (PnLDashboard)
  #market (MarketPrices)
  #forecast (PriceForecast)
  #schemes (SchemeMatcher)
  #insurance (InsuranceClaims)
* (404 Not Found)
```

### 8.4 Global UI Elements

- **Toast System:** Radix UI toast with auto-dismiss (5s default). Types: default, destructive. Position: bottom-right.
- **Error Boundary:** Global React ErrorBoundary wrapping entire app. Shows fallback UI with "Something went wrong" and refresh button.
- **Loading:** Loader2 spinner (Lucide) for full-page loading. Skeleton screens for data-loading states. Component-level loading spinners for individual data fetches.

---

## 9. INTEGRATIONS

### 9.1 Google Earth Engine

- **Purpose:** Satellite-derived vegetation indices, soil moisture, temperature, rainfall
- **Authentication:** GCP service account JSON key referenced by `GOOGLE_APPLICATION_CREDENTIALS` env var. Initialized via `ee.Initialize(project=GEE_PROJECT)`.
- **Data Sources:** Sentinel-2 (10m resolution, 5-day revisit), MODIS (250m), ERA5 (climate), SMAP/FLDAS (soil)
- **Data Flow:** Backend sends field polygon → EE computes median indices over polygon for date range → returns JSON time series
- **Error Handling:** Returns 503 with error details if EE unavailable. Cached initialization status.
- **Rate Limit:** 20 req/hour per user

### 9.2 OpenWeatherMap

- **Purpose:** Current weather conditions and 5-day forecasts
- **Authentication:** API key via `OPENWEATHER_API_KEY` env var
- **Endpoints Used:** `api.openweathermap.org/data/2.5/weather`, `/forecast`
- **Data Flow:** Frontend sends field coordinates → OWM returns temperature, humidity, wind, description, icon
- **Error Handling:** Celery task retries 3 times with 60s delay on failure
- **Fallback:** Weather widget shows "Weather unavailable" if API fails

### 9.3 Google Gemini AI

- **Purpose:** Agricultural chatbot (gemini-2.5-flash) + image validation for pest uploads (gemini-2.0-flash) + soil advice generation
- **Authentication:** API key via `GEMINI_API_KEY` env var, configured at module load and lazy-checked at request time
- **Error Handling:** Returns 502 for Gemini errors, 503 if not configured
- **Rate Limit:** 60 chat requests/hour per user

### 9.4 data.gov.in / Agmarknet

- **Purpose:** Live agricultural commodity market prices from Indian mandis
- **Endpoints Used:** data.gov.in API for agricultural market data
- **Error Handling:** Returns empty list or cached data if API unavailable

---

## 10. BACKGROUND JOBS & SCHEDULED TASKS

| Job | Trigger | Purpose | Retry | Lock |
|-----|---------|---------|-------|------|
| `update_weather_data` | Every 6 hours | Fetch weather for all fields, create FieldLog entries | 3 retries, 60s delay | Redis lock (1200s timeout) |
| `update_satellite_data` | Daily at 2 AM | Refresh EE satellite indices for all fields | 3 retries, 120s delay | — |
| `calculate_risk_scores` | Daily at 3 AM | Run LSTM risk prediction, create FieldAlerts for high-risk fields (score > 0.6) | 3 retries, 120s delay | — |
| `generate_daily_reports` | Daily at 6 AM | Create inactivity alerts for fields with no logs in 7+ days | — | — |
| `cleanup_old_logs` | Weekly (Sunday 1 AM) | Delete FieldLog entries older than 730 days (configurable via `LOG_RETENTION_DAYS`) | — | — |

All tasks use `@shared_task` for Celery. Concurrent runs prevented via Redis-based `task_lock` decorator using `cache.add()`.

---

## 11. NOTIFICATIONS & COMMUNICATIONS

| Type | Trigger | Recipient | Content | Timing |
|------|---------|-----------|---------|--------|
| In-app Alert | FieldLog created | Field owner | Activity-specific tip (e.g., "Watering logged. Next: check after 3 days") | Immediate |
| In-app Alert | High risk detected (risk > 0.6) | Field owner | "High risk detected for {field}: {level} (score: X.XX)" | Daily (3 AM task) |
| In-app Alert | No activity in 7+ days | Field owner | "No activity logged for {field} in N days" | Daily (6 AM task) |
| In-app Toast | Session expired | Current user | "Session Expired. Please log in again." | On 401 response |
| Email | Password reset | Requesting user | Subject: "Reset your KrishiSaarthi password" / Body: reset link | Immediate |
| Email | Email verification | New user | Subject: "Verify your KrishiSaarthi account" / Body: verification link | On signup |
| In-app Badge | Unread alerts exist | Current user | Numeric badge on notification bell (max "9+") | Polled every 60s |

---

## 12. ERROR HANDLING STRATEGY

### Frontend
- **Global Error Boundary:** `ErrorBoundary` component wraps the entire app. Catches React render errors. Displays "Something went wrong" with refresh button.
- **API Error Handling:** `apiFetch()` in `api.ts` implements:
  - Timeout handling (30s default, AbortController)
  - Retry logic (2 retries for 5xx errors with exponential backoff)
  - `ApiError` class with `status`, `message`, `details`
  - Global 401 handler (debounced `fireUnauthorized`) triggers auto-logout
  - No retry for auth errors (401/403)
- **Form Validation:** Zod schemas + React Hook Form. Errors displayed inline below fields.
- **404 Page:** Custom not-found page accessible at catch-all route
- **Network Error:** Toast: "Network error. Unable to connect to server."

### Backend
- **Standard Error Envelope:** `{"error": "message"}` or `{"error": "message", "details": "..."}`
- **DRF Validation Errors:** `{"field_name": ["error message"]}` (400)
- **Logging:** Python logging module with structured format. ERROR for exceptions, WARNING for expected failures, INFO for significant events.
- **Unhandled Exceptions:** Caught at view level, logged with traceback, return 500 with generic message (no stack trace in response).

---

## 13. PERFORMANCE REQUIREMENTS

| Metric | Target |
|--------|--------|
| Initial page load (desktop) | < 3s (LCP) |
| API latency (non-ML, P95) | < 300 ms |
| API latency (ML endpoints, P95) | < 15 s |
| EE endpoint latency (P95) | < 20s |
| Concurrent users | 100+ |
| Database query time (max) | < 100 ms |
| Bundle size (gzipped) | < 500 KB initial |

**Caching Strategy:**
- Redis cache for EE data (TTL: 1 hour)
- Rate limit counters in Redis
- Celery task locks in Redis
- Frontend lazy-loads all pages (`React.lazy`)
- Manual Vite chunk splitting for leaflet, recharts, jspdf, radix

**Asset Optimization:**
- Code splitting by route (lazy loading)
- Tree shaking via Vite/esbuild
- Production: `console` and `debugger` statements stripped
- Google Fonts loaded from external CDN with caching

---

## 14. SECURITY REQUIREMENTS

| Area | Implementation |
|------|---------------|
| **Authentication** | Knox token-based. One token per session. Tokens invalidated on logout. |
| **Password Storage** | Django PBKDF2-SHA256 hashing with salt |
| **Input Validation** | DRF serializers validate all inputs. Polygon validator for GeoJSON. Image type/size validation. |
| **CORS** | `django-cors-headers` with explicit allowed origins (configurable via `CORS_ALLOWED_ORIGINS`) |
| **Rate Limiting** | Per-endpoint throttling via DRF throttle classes. Login: 5/min. ML: 30/hour. Chat: 60/hour. |
| **Data Encryption at Rest** | Fernet symmetric encryption for PII fields (bank_account, ifsc_code) |
| **SQL Injection** | Prevented by Django ORM (parameterized queries) |
| **XSS** | React's default escaping + DRF JSON serialization |
| **CSRF** | DRF uses token auth (stateless), CSRF not applicable |
| **IDOR Prevention** | All views filter by `request.user`. Chat sessions verified for ownership. |
| **File Upload Security** | Type whitelist (JPEG/PNG), size limit (10MB), Gemini validation |
| **Session Security** | 30-min inactivity timeout (client-side). Token rotation on re-login. |
| **Secrets Management** | All secrets via environment variables. `.env` files in `.gitignore`. |
| **Audit Logging** | Request logging middleware captures method, path, status, duration |
| **Dependency Scanning** | requirements.txt pinned versions. Manual review cadence. |

---

## 15. TESTING REQUIREMENTS

| Module | Unit Tests | Integration Tests | E2E Tests |
|--------|-----------|------------------|-----------|
| Auth (login/signup/logout) | Password validation, throttle, token creation | Full login→dashboard flow | Login→navigate→logout |
| Field CRUD | Polygon validation, model creation | Create field→fetch→delete | Map polygon draw→save→verify |
| Pest Detection | CNN inference, image validation | Upload image→validate→detect | Upload photo→see results |
| Health Score | Score computation, weight validation | EE fetch→CNN→LSTM→score fusion | View dashboard health gauge |
| Chat | Session creation, message persistence | Send message→receive reply | Open chat→ask question→see answer |
| Finance | Revenue auto-calc, cost categories | Create cost→create revenue→view P&L | Full expense tracking flow |
| Inventory | Stock validation, F() atomic updates | Purchase→use→check stock | Add item→record usage→verify |
| Insurance | Encrypted field storage/retrieval | Create claim→update status | Submit claim→check status |
| Equipment | Overlap booking detection | Book→attempt overlap→error | Schedule equipment for field |

**Coverage Target:** ≥ 80% line coverage for backend business logic. Frontend: component rendering tests for critical views.

---

## 16. ENVIRONMENT & CONFIGURATION

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | Yes | — | Django secret key (64+ random chars) |
| `DEBUG` | No | True | Debug mode (False in production) |
| `ALLOWED_HOSTS` | No | localhost,127.0.0.1 | Comma-separated allowed hosts |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection URL |
| `REDIS_URL` | No | redis://127.0.0.1:6379/0 | Redis connection URL |
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `OPENWEATHER_API_KEY` | Yes | — | OpenWeatherMap API key |
| `GOOGLE_APPLICATION_CREDENTIALS` | Yes (prod) | — | Path to GCP service account JSON |
| `GEE_PROJECT` | Yes (prod) | — | Google Earth Engine project ID |
| `CORS_ALLOWED_ORIGINS` | No | http://localhost:5173,... | CORS allowed origins |
| `EMAIL_HOST` | No (prod: Yes) | smtp.gmail.com | SMTP server |
| `EMAIL_PORT` | No | 587 | SMTP port |
| `EMAIL_USE_TLS` | No | True | Use TLS for email |
| `EMAIL_HOST_USER` | No (prod: Yes) | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | No (prod: Yes) | — | SMTP password |
| `FRONTEND_URL` | No | http://localhost:5173 | Frontend URL (for email links) |
| `DJANGO_SUPERUSER_USERNAME` | No | admin | Admin user (init_db.py) |
| `DJANGO_SUPERUSER_EMAIL` | No | admin@krishisaarthi.com | Admin email |
| `DJANGO_SUPERUSER_PASSWORD` | Yes (init) | — | Admin password |
| `SECURE_SSL_REDIRECT` | No | False | Force HTTPS redirect |
| `POSTGRES_DB` | No (Docker) | krishisaarthi | PostgreSQL database name |
| `POSTGRES_USER` | No (Docker) | krishiuser | PostgreSQL username |
| `POSTGRES_PASSWORD` | Yes (Docker) | — | PostgreSQL password |
| `VITE_API_BASE_URL` | No | "" (uses proxy) | Backend API URL for frontend |

---

## 17. IMPLEMENTATION CHECKLIST

### Backend
- [x] Django project setup (KrishiSaarthi)
- [x] Knox token authentication
- [x] Login/Signup/Logout/TestToken views with rate limiting
- [x] Password reset flow with email
- [x] Email verification flow
- [x] Field app: FieldData CRUD with polygon validation
- [x] Field app: Earth Engine integration (fetchEEData)
- [x] Field app: Pest detection (CNN MobileNetV2)
- [x] Field app: Gemini image validation
- [x] Field app: LSTM risk prediction
- [x] Field app: AWD detection
- [x] Field app: Carbon credit calculation
- [x] Field app: Health score fusion
- [x] Field app: Weather view (OWM proxy)
- [x] Field app: Field logs CRUD
- [x] Field app: Field alerts with bulk mark-read
- [x] Field app: Irrigation schedule + logs
- [x] Field app: Yield prediction
- [x] Field app: Soil advice (Gemini)
- [x] Field app: Diagnose health endpoint
- [x] Finance app: Season CRUD
- [x] Finance app: Cost entry CRUD with summary
- [x] Finance app: Revenue CRUD with auto-calculation
- [x] Finance app: P&L dashboard aggregation
- [x] Finance app: Market prices (data.gov.in)
- [x] Finance app: Price forecast (LSTM)
- [x] Finance app: Government schemes CRUD (admin) + read (user)
- [x] Finance app: Insurance claims with encrypted PII
- [x] Finance app: Finance transaction ledger (ViewSet)
- [x] Planning app: Season calendar CRUD
- [x] Planning app: Inventory CRUD with atomic stock updates
- [x] Planning app: Inventory transactions with stock validation
- [x] Planning app: Labor management with wage auto-calc
- [x] Planning app: Equipment registry CRUD
- [x] Planning app: Equipment booking with overlap prevention
- [x] Planning app: Crop rotation planner (rule-based)
- [x] Planning app: Plan model (ViewSet)
- [x] Chat app: Gemini-powered chatbot with session management
- [x] Chat app: History retrieval and deletion
- [x] ML engine: CNN model loading and inference
- [x] ML engine: LSTM model loading and inference
- [x] ML engine: Health score computation
- [x] ML engine: Model registry with file tracking
- [x] Config: Rate limiting classes (7 throttle types)
- [x] Config: Fernet encryption for PII fields
- [x] Config: Structured logging
- [x] Config: Redis caching
- [x] Middleware: Request logging
- [x] Health checks: /health, /ready, /metrics
- [x] Celery tasks: 5 background jobs with locks
- [x] API documentation: drf-spectacular (Swagger + ReDoc)
- [x] Prometheus metrics integration
- [x] Dockerfile + entrypoint.sh

### Frontend
- [x] Vite + React 18 + TypeScript setup
- [x] TailwindCSS + shadcn/ui component library
- [x] AuthContext with Knox token management and 401 handling
- [x] FieldContext with field state management
- [x] API client (apiFetch) with retry, timeout, debounced 401
- [x] Landing page (public)
- [x] Login page with validation
- [x] Signup page with validation
- [x] Password reset flow (request + confirm)
- [x] Dashboard shell (sidebar + header + content area)
- [x] HomeDashboard overview (weather, health, market prices, quick actions)
- [x] MyField component (field list + add)
- [x] MapView with Leaflet polygon drawing
- [x] FieldReport with satellite indices charts
- [x] DataAnalytics multi-chart dashboard
- [x] Pest detection: image upload + CNN results display
- [x] FieldLog: activity log CRUD
- [x] FieldAlerts: alert list with mark-read
- [x] IrrigationScheduler: schedule view + log CRUD
- [x] YieldPrediction: estimation UI
- [x] CostCalculator: full expense CRUD
- [x] PnLDashboard: P&L charts
- [x] MarketPrices: mandi price table
- [x] PriceForecast: trend charts
- [x] SchemeMatcher: eligibility-based scheme discovery
- [x] InsuranceClaims: claim CRUD + status tracking
- [x] SeasonCalendar: calendar view with activity planning
- [x] InventoryTracker: item CRUD + transactions
- [x] LaborManager: worker/wage CRUD
- [x] EquipmentScheduler: equipment registry + booking
- [x] RotationPlanner: rotation planning UI
- [x] ChatBot: floating chatbot with Gemini
- [x] Voice recording input (useVoiceRecording)
- [x] Weather widget (useWeather)
- [x] Health gauge (useHealthScore)
- [x] ThemeProvider (dark/light mode)
- [x] ErrorBoundary (global)
- [x] ExportButton (PDF/Excel)
- [x] PWA manifest + service worker
- [x] 404 page
- [x] Responsive design (mobile sidebar toggle)

### Infrastructure
- [x] docker-compose.yml (dev)
- [x] docker-compose.prod.yml (production)
- [x] Backend Dockerfile
- [x] Frontend Dockerfile + nginx.conf
- [x] .env.example with all variables
- [x] Prometheus monitoring setup

### Tests
- [x] pytest configuration (pytest.ini)
- [x] Auth flow tests (test_auth_flows.py)
- [ ] Full E2E test suite
- [ ] Performance/load tests

### Documentation
- [x] README.md
- [x] TROUBLESHOOTING.md
- [x] API docs (auto-generated via drf-spectacular)
- [x] This project report

---

## 18. OPEN QUESTIONS

| # | Question | Owner | Deadline |
|---|----------|-------|----------|
| 1 | Should email verification be mandatory in production? | Product Owner | Before production deploy |
| 2 | What is the Knox token TTL? Should it be shorter than the 30-min frontend timeout? | Security Lead | Before production deploy |
| 3 | Should the PlantVillage CNN model be retrained with Indian crop varieties? | ML Engineer | Post-launch |
| 4 | Is the data.gov.in market price API reliable enough, or should a scraping fallback be implemented? | Backend Lead | Before launch |
| 5 | Should insurance claim status transitions be restricted (e.g., only admin can move to "approved")? | Product Owner | Before launch |
| 6 | What PostgreSQL backup strategy should be used in production? | DevOps | Before production deploy |
| 7 | Should Celery beat schedule be configured in code or via Django admin? | Backend Lead | Before production deploy |

---

## 19. GLOSSARY

| Term | Definition |
|------|-----------|
| **NDVI** | Normalized Difference Vegetation Index — satellite-derived measure of vegetation greenness (0.0–1.0). Higher = healthier crops. |
| **EVI** | Enhanced Vegetation Index — improved NDVI reducing atmospheric and soil background effects. |
| **SAVI** | Soil Adjusted Vegetation Index — vegetation index corrected for soil brightness. |
| **NDWI** | Normalized Difference Water Index — measures water content in vegetation/soil. |
| **AWD** | Alternate Wetting and Drying — rice irrigation technique that reduces water use and methane emissions. |
| **Knox Token** | Django REST Knox authentication token — per-session, database-backed, with configurable expiry. |
| **Mandi** | Indian agricultural market/marketplace. |
| **PMFBY** | Pradhan Mantri Fasal Bima Yojana — India's national crop insurance scheme. |
| **Kharif** | Indian monsoon cropping season (June–October). |
| **Rabi** | Indian winter cropping season (October–March). |
| **Zaid** | Indian summer cropping season (March–June). |
| **GEE** | Google Earth Engine — cloud-based geospatial analysis platform. |
| **MobileNetV2** | Lightweight CNN architecture optimized for mobile inference. |
| **LSTM** | Long Short-Term Memory — recurrent neural network for sequence prediction. |
| **Fernet** | Symmetric encryption scheme from the Python `cryptography` library. |
| **Sentinel-2** | ESA satellite constellation providing 10m resolution multispectral imagery. |
| **PlantVillage** | Public dataset of 54,000+ plant leaf images across 38 disease classes. |

---

## 20. REVISION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-11 | Antigravity AI | Initial comprehensive report, reverse-engineered from full codebase analysis |
