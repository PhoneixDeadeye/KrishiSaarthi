# AgriSmart (KrishiSaarthi) — Complete Improvement Report
## From Current State to Production-Ready, Real-World Deployment

**Generated:** March 8, 2026  
**Scope:** Full-stack audit — Backend, Frontend, ML Engine, DevOps, Security, Testing, Performance, UX  
**Total Findings:** 147 items across 14 categories

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Assessment](#2-current-state-assessment)
3. [PHASE 1 — Critical Security Fixes (Week 1)](#3-phase-1--critical-security-fixes-week-1)
4. [PHASE 2 — Backend Bug Fixes & Validation (Week 2)](#4-phase-2--backend-bug-fixes--validation-week-2)
5. [PHASE 3 — Frontend Fixes & UX Completion (Week 2–3)](#5-phase-3--frontend-fixes--ux-completion-week-23)
6. [PHASE 4 — API Design & Data Integrity (Week 3)](#6-phase-4--api-design--data-integrity-week-3)
7. [PHASE 5 — Performance Optimization (Week 4)](#7-phase-5--performance-optimization-week-4)
8. [PHASE 6 — Testing & Quality Assurance (Week 4–5)](#8-phase-6--testing--quality-assurance-week-45)
9. [PHASE 7 — DevOps & CI/CD Pipeline (Week 5–6)](#9-phase-7--devops--cicd-pipeline-week-56)
10. [PHASE 8 — Monitoring & Observability (Week 6)](#10-phase-8--monitoring--observability-week-6)
11. [PHASE 9 — ML Engine Hardening (Week 7)](#11-phase-9--ml-engine-hardening-week-7)
12. [PHASE 10 — Production Deployment Checklist (Week 7–8)](#12-phase-10--production-deployment-checklist-week-78)
13. [PHASE 11 — Customer-Readiness & Polish (Week 8–9)](#13-phase-11--customer-readiness--polish-week-89)
14. [PHASE 12 — Documentation & Handoff (Week 9–10)](#14-phase-12--documentation--handoff-week-910)
15. [Full Issue Tracker](#15-full-issue-tracker)
16. [Architecture Recommendations](#16-architecture-recommendations)

---

## 1. Executive Summary

AgriSmart is an impressive full-stack agricultural platform combining Django REST Framework, React/TypeScript, PyTorch ML models, Google Earth Engine satellite analysis, Gemini AI integration, and Docker-based deployment. The foundation is **solid but not production-ready**.

### Scorecard (Current State)

| Category | Score | Status |
|----------|-------|--------|
| **Security** | 4/10 | Critical vulnerabilities in auth, data encryption, token management |
| **Backend Code Quality** | 6/10 | Good structure with validation gaps and logic bugs |
| **Frontend Code Quality** | 5/10 | Good UI but many non-functional elements, silent failures |
| **API Design** | 5/10 | Functional but inconsistent, no pagination, no versioning |
| **Testing** | 3/10 | 105 tests exist but ~40% of endpoints are untested |
| **DevOps/CI/CD** | 2/10 | Docker setup exists but no CI/CD, broken monitoring |
| **Performance** | 4/10 | Synchronous ML, no batching, unbounded queries |
| **ML Engine** | 7/10 | Well-structured with good fallbacks, minor data pipeline issues |
| **Monitoring** | 1/10 | Config exists but nothing actually works |
| **Documentation** | 6/10 | Good README but missing API docs, deployment guides |
| **UX/Accessibility** | 4/10 | Beautiful UI with dead elements and no accessibility |
| **i18n** | 3/10 | System exists but 80% of strings are hardcoded English |
| **Overall** | **3.8/10** | **Not ready for production customer base** |

### Target Scorecard (After Improvements)

| Category | Target | How |
|----------|--------|-----|
| **Security** | 9/10 | Token expiry, encryption, no data leaks |
| **Backend** | 9/10 | All validation gaps fixed, consistent patterns |
| **Frontend** | 9/10 | All UI functional, proper error handling, React Query |
| **API Design** | 9/10 | RESTful, paginated, versioned, documented |
| **Testing** | 8/10 | 90%+ endpoint coverage, edge cases, CI gates |
| **DevOps** | 9/10 | Full CI/CD, automated deployment |
| **Performance** | 8/10 | Async ML, batched tasks, pagination |
| **ML Engine** | 9/10 | Batched inference, proper temporal data |
| **Monitoring** | 8/10 | Working Prometheus + Grafana + alerts |
| **Documentation** | 9/10 | Full API docs, deployment guide, user manual |
| **UX/A11y** | 8/10 | WCAG 2.1 AA, keyboard nav, screen reader support |
| **i18n** | 8/10 | All strings translated, language persistence |
| **Overall** | **8.8/10** | **Production-ready for real customers** |

---

## 2. Current State Assessment

### What's Working Well
- **Architecture**: Clean separation of concerns (Django apps, React components, ML engine isolated, Docker multi-service)
- **ML Engine**: MobileNetV2 CNN, LSTM risk prediction, health score fusion — all with lazy loading and graceful fallbacks
- **API Layer** (frontend): centralized `apiFetch()` with retry, backoff, timeout, typed errors
- **Auth Foundation**: Token-based authentication, IDOR protection on every endpoint
- **Security Basics**: Rate limiting (4 throttle classes), CORS locked down, production hardening settings, security headers
- **UI Design**: Beautiful Tailwind/shadcn interface, responsive design, dark mode support

### What's Broken Right Now
- Rabi season detection always returns "Zaid" (always-false condition)
- Chat context window retrieves oldest 20 messages instead of newest 20
- Dashboard search bar does nothing
- Map overlay buttons ("Satellite", "NDVI Layer") do nothing
- P&L Dashboard "Export" and "Add Entry" buttons do nothing
- Market price search input does nothing
- Agro Alerts section always shows "No alerts" (dead state)
- Data Analytics shows hardcoded `₹2,700` market price and `0` tree count
- NDWI chart shows hardcoded static data regardless of actual data
- Language choice resets on every page reload
- Weather task fetches data then throws it away
- Risk calculation task computes scores then throws them away

---

## 3. PHASE 1 — Critical Security Fixes (Week 1)

> **Priority: MANDATORY before any deployment. These are exploitable vulnerabilities.**

### 1.1 — Implement Token Expiry
**File:** `backend/KrishiSaarthi/views.py` + new middleware  
**Current:** `rest_framework.authtoken` tokens never expire — stolen token has indefinite access.  
**Fix:**
```
Step 1: Install django-rest-knox (pip install django-rest-knox)
Step 2: Replace rest_framework.authtoken with knox in INSTALLED_APPS
Step 3: Update Login view to use knox.views.LoginView
Step 4: Add TOKEN_TTL = timedelta(hours=24) in settings
Step 5: Add auto-refresh middleware that extends token on activity
Step 6: Update frontend to handle 401 by refreshing or re-login
```

### 1.2 — Encrypt Sensitive Financial Data
**Files:** `backend/finance/models.py`, `backend/finance/views/insurance.py`  
**Current:** `bank_account` and `ifsc_code` stored as plaintext `CharField`.  
**Fix:**
```
Step 1: pip install django-fernet-fields
Step 2: Change bank_account to EncryptedCharField(max_length=20)
Step 3: Change ifsc_code to EncryptedCharField(max_length=11)
Step 4: Add FERNET_KEY to settings (sourced from env var)
Step 5: Create migration
Step 6: Mask bank_account in all API responses (show only last 4 digits)
Step 7: Add data migration to encrypt existing plaintext data
```

### 1.3 — Fix Password Reset User Enumeration
**File:** `backend/KrishiSaarthi/views.py`, class `RequestPasswordReset`  
**Current:** Returns `404 "User not found"` — tells attacker which emails are registered.  
**Fix:**
```python
# ALWAYS return success regardless of user existence
return Response({
    'message': 'If an account exists with this email, a password reset link has been sent.'
}, status=status.HTTP_200_OK)
```

### 1.4 — Add Password Validation on Reset
**File:** `backend/KrishiSaarthi/views.py`, class `ResetPassword`  
**Current:** `user.set_password(password)` accepts ANY string — empty, single char, etc.  
**Fix:**
```python
from django.contrib.auth.password_validation import validate_password
try:
    validate_password(password, user)
except ValidationError as e:
    return Response({'errors': e.messages}, status=400)
user.set_password(password)
```

### 1.5 — Fix Login Timing Side-Channel
**File:** `backend/KrishiSaarthi/views.py`, class `Login`  
**Current:** If username doesn't exist, response is fast. If it exists but password is wrong, `check_password()` is slow. Attacker can enumerate valid usernames.  
**Fix:**
```python
from django.contrib.auth import authenticate
user = authenticate(username=username, password=password)
if user is None:
    return Response({'error': 'Invalid credentials'}, status=401)
```

### 1.6 — Server-Side Token Validation on Frontend Mount
**File:** `frontend/client/src/context/AuthContext.tsx`  
**Current:** Token validation on mount exists but is fire-and-forget. If it fails, user stays "logged in" until an API call fails.  
**Fix:**
```
Step 1: In the token validation useEffect, await the server response
Step 2: If /test_token returns 401, call logout() immediately
Step 3: Show a loading spinner until validation completes
Step 4: Only render children once auth state is resolved
```

### 1.7 — Server-Side Logout (Token Deletion)
**File:** `frontend/client/src/context/AuthContext.tsx`  
**Current:** `logout()` only clears localStorage. The Django token survives and can still be used.  
**Fix:**
```
Step 1: Await the POST /logout call (currently fire-and-forget)
Step 2: Only clear localStorage AFTER server confirms deletion
Step 3: Handle case where server is unreachable (clear locally anyway)
```

### 1.8 — Fix Docker Password Defaults
**Files:** `docker-compose.yml`, `docker-compose.prod.yml`  
**Current:** `docker-compose.yml` may have `POSTGRES_PASSWORD=changeme` default. Grafana uses `admin`.  
**Fix:**
```yaml
# docker-compose.yml — require password via .env
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}

# docker-compose.prod.yml — require Grafana password
GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:?Set GRAFANA_PASSWORD in .env}
```

### 1.9 — Remove Source Code Volume Mount in Production
**File:** `docker-compose.prod.yml`  
**Current:** `./backend:/app` volume mount means prod runs host files, not the Docker image.  
**Fix:** Remove `- ./backend:/app` from the backend service. Keep only `media`, `logs`, and `ml_models` mounts.

### 1.10 — Restrict PostgreSQL Port Exposure
**File:** `docker-compose.yml`  
**Current:** Port 5432 exposed to all interfaces.  
**Fix:** Already using commented-out port in current `docker-compose.yml` — verify it stays commented in production.

### 1.11 — Add Global 401 Interceptor in Frontend
**File:** `frontend/client/src/lib/api.ts` or `frontend/client/src/App.tsx`  
**Current:** When token expires mid-session, no global handler catches 401 errors.  
**Fix:**
```
Step 1: Add global error handler in React Query's queryClient
Step 2: On any 401 response, dispatch a logout event
Step 3: AuthContext listens for the event and clears state
Step 4: Redirect to /login with "Session expired" message
```

### 1.12 — Add Email Verification on Signup
**Files:** `backend/KrishiSaarthi/views.py`, new template  
**Current:** Users register with any email, no verification.  
**Fix:**
```
Step 1: Add is_email_verified field to User model (or profile)
Step 2: On signup, set is_active=False and send verification email
Step 3: Create /verify-email/<token> endpoint
Step 4: On verification, set is_active=True
Step 5: Block login for unverified accounts with clear message
Step 6: Add resend-verification endpoint
```

### 1.13 — Restrict /metrics Endpoint to Admins
**File:** `backend/KrishiSaarthi/health.py`  
**Current:** `permission_classes = [IsAuthenticated]` — any logged-in user sees system metrics.  
**Fix:** Change to `permission_classes = [IsAdminUser]`.

### 1.14 — Fix ErrorBoundary Information Leakage
**File:** `frontend/client/src/components/common/ErrorBoundary.tsx`  
**Current:** Raw `error.message` rendered to user — could contain stack traces, DB details.  
**Fix:**
```
Step 1: Show generic "Something went wrong" message to users
Step 2: Log the real error via logger.error()
Step 3: In development mode only, optionally show details
```

---

## 4. PHASE 2 — Backend Bug Fixes & Validation (Week 2)

### 2.1 — Fix Rabi Season Logic (Always-False Condition)
**File:** `backend/planning/views/rotation.py`, Lines 166–169  
**Current:** `elif 11 <= month <= 3` — always False.  
**Fix:** `elif month >= 11 or month <= 3:`

### 2.2 — Fix Chat Context Window (Oldest vs Newest Messages)
**File:** `backend/chat/views.py`, Line 63  
**Current:** `.order_by('timestamp')[:20]` — gets first 20 messages.  
**Fix:** `.order_by('-timestamp')[:20]` then `list(reversed(...))` to get last 20 messages in chronological order.

### 2.3 — Fix Irrigation Fallback Coordinates
**File:** `backend/field/views/irrigation.py`, ~Line 114  
**Current:** Silently falls back to `lat, lng = 10.0, 76.0` (Kerala) when field has no coordinates.  
**Fix:**
```python
if not lat or not lng:
    return Response({
        'error': 'Field location not set. Please save your field coordinates first.'
    }, status=400)
```

### 2.4 — Fix `datetime.now()` → `timezone.now()`
**File:** `backend/field/views/irrigation.py`, ~Line 148  
**Fix:** `from django.utils import timezone; now = timezone.now()`

### 2.5 — Fix Schemes Auto-Seed Race Condition
**File:** `backend/finance/views/schemes.py`, Lines ~157–158  
**Current:** Two concurrent requests both see empty table and both seed.  
**Fix:**
```
Step 1: Move seeding to a Django management command: python manage.py seed_schemes
Step 2: Run the management command in Dockerfile or entrypoint
Step 3: Remove runtime seeding from the view
```

### 2.6 — Fix Insurance Claims — Use Serializer Instead of Manual Validation
**File:** `backend/finance/views/insurance.py`  
**Fix:**
```
Step 1: Create InsuranceClaimSerializer with proper field definitions
Step 2: Add field-level validators (positive amounts, valid dates, etc.)
Step 3: Replace manual POST handler with serializer.is_valid() pattern
Step 4: Replace PATCH setattr() loop with serializer partial update
```

### 2.7 — Fix Price Forecast Unvalidated int() Cast
**File:** `backend/finance/views/price_forecast.py`, ~Line 76  
**Current:** `days = int(request.query_params.get('days', 30))` — crashes on non-integer.  
**Fix:**
```python
try:
    days = int(request.query_params.get('days', 30))
    if days < 1 or days > 365:
        return Response({'error': 'Days must be between 1 and 365'}, status=400)
except (ValueError, TypeError):
    return Response({'error': 'Invalid days parameter'}, status=400)
```

### 2.8 — Fix PnL Dashboard Error Handling
**File:** `backend/finance/views/pnl_dashboard.py`  
**Fix:** Wrap entire GET handler in try/except with proper error response.

### 2.9 — Fix Soil Advice Input Validation
**File:** `backend/field/views/soil_advice.py`  
**Fix:**
```python
validators = {
    'nitrogen': (0, 500, 'kg/ha'),
    'phosphorus': (0, 200, 'kg/ha'),
    'potassium': (0, 600, 'kg/ha'),
    'ph': (0, 14, ''),
}
for key, (min_val, max_val, unit) in validators.items():
    value = data.get(key)
    if value is not None and not (min_val <= float(value) <= max_val):
        return Response({'error': f'{key} must be between {min_val} and {max_val}'}, status=400)
```

### 2.10 — Fix DELETE Endpoints Return Codes
**Files:** `cost_calculator.py`, `revenue.py`, `season.py`, all planning DELETE handlers  
**Fix:** Change all `Response({'message': '...'}, status=200)` to `Response(status=status.HTTP_204_NO_CONTENT)`.

### 2.11 — Fix Market Prices Bare 500 Status
**File:** `backend/finance/views/market_prices.py`, ~Line 107  
**Fix:** `return Response(..., status=status.HTTP_500_INTERNAL_SERVER_ERROR)`.

### 2.12 — Fix `getCoord` Class Naming (PEP 8)
**File:** `backend/field/views/field_crud.py`, ~Line 105 + `backend/field/urls.py`  
**Fix:** Rename to `GetCoord` in both files.

### 2.13 — Fix Signup Double-Save
**File:** `backend/KrishiSaarthi/serializers.py` + `backend/KrishiSaarthi/views.py`  
**Fix:**
```python
# In UserSerializer:
def create(self, validated_data):
    user = User.objects.create_user(
        username=validated_data['username'],
        email=validated_data.get('email', ''),
        password=validated_data['password']
    )
    return user

# In Signup view: just call serializer.save() once
```

### 2.14 — Add Email Uniqueness Validation
**File:** `backend/KrishiSaarthi/serializers.py`  
**Fix:**
```python
from rest_framework.validators import UniqueValidator
email = serializers.EmailField(
    validators=[UniqueValidator(queryset=User.objects.all())]
)
```

### 2.15 — Fix IrrigationLog — Add Serializer Validation
**File:** `backend/field/views/irrigation.py`  
**Fix:**
```
Step 1: Create IrrigationLogSerializer with proper field types
Step 2: Validate water_amount > 0, duration_minutes > 0
Step 3: Validate date is not in the future
Step 4: Validate source against IrrigationSource choices
Step 5: Replace direct objects.create() with serializer.save()
```

### 2.16 — Fix Weather Task — Actually Store Data
**File:** `backend/field/tasks.py`  
**Current:** `update_weather_data` calls the weather API but discards the response.  
**Fix:**
```
Step 1: Create a WeatherCache model (field, data, fetched_at)
Step 2: Store the weather response in the cache model
Step 3: Or store in Redis cache with field-specific key
Step 4: Set a 6-hour TTL matching the task frequency
```

### 2.17 — Fix Risk Scores Task — Persist Results
**File:** `backend/field/tasks.py`  
**Current:** `calculate_risk_scores` computes risk but doesn't save it.  
**Fix:**
```
Step 1: Add risk_score field to FieldData model (or create FieldRisk model)
Step 2: Save the computed risk score after calculation
Step 3: Use this stored value in health score computation
```

### 2.18 — Fix Inventory Negative Stock
**File:** `backend/planning/models.py`  
**Fix:**
```python
# Add check constraint:
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(quantity__gte=0),
            name='inventory_quantity_non_negative'
        )
    ]

# In InventoryTransaction.save(), validate before saving:
if self.transaction_type == 'use':
    current = InventoryItem.objects.select_for_update().get(id=self.item_id)
    if current.quantity < self.quantity:
        raise ValidationError('Insufficient stock')
```

### 2.19 — Fix Equipment Booking Overlap
**File:** `backend/planning/models.py` or `backend/planning/views/equipment.py`  
**Fix:**
```python
# In EquipmentBooking clean() or save():
overlapping = EquipmentBooking.objects.filter(
    equipment=self.equipment,
    start_date__lt=self.end_date,
    end_date__gt=self.start_date,
).exclude(pk=self.pk)
if overlapping.exists():
    raise ValidationError('Equipment is already booked for this period')
```

### 2.20 — Fix Revenue Auto-Calculation Edge Case
**File:** `backend/finance/models.py`, Revenue model  
**Fix:** Always recalculate `total_amount` in `save()`, not just on create.
```python
def save(self, *args, **kwargs):
    if self.quantity_sold and self.price_per_unit:
        self.total_amount = self.quantity_sold * self.price_per_unit
    super().save(*args, **kwargs)
```

### 2.21 — Add Pagination to All List Endpoints
**Files:** All views that return lists  
**Fix:**
```
Step 1: DRF PageNumberPagination is already configured (PAGE_SIZE=50)
Step 2: For APIView-based views, add manual pagination:
   paginator = PageNumberPagination()
   result_page = paginator.paginate_queryset(queryset, request)
   serializer = MySerializer(result_page, many=True)
   return paginator.get_paginated_response(serializer.data)
Step 3: Update all list endpoints in: field_crud.py, logs_alerts.py,
   cost_calculator.py, revenue.py, season.py, insurance.py, schemes.py,
   calendar.py, inventory.py, labor.py, equipment.py
Step 4: Update frontend to handle paginated responses (next/previous links)
```

### 2.22 — Add Bulk Mark-All-Read Endpoint for Alerts
**File:** `backend/field/views/logs_alerts.py` + `backend/field/urls.py`  
**Fix:**
```python
class BulkMarkAlertsReadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, field_id):
        count = FieldAlert.objects.filter(
            field__id=field_id, field__user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked': count})
```

---

## 5. PHASE 3 — Frontend Fixes & UX Completion (Week 2–3)

### 3.1 — Fix Non-Functional Dashboard Search
**File:** `frontend/client/src/pages/Dashboard.tsx`, Lines ~188–194  
**Fix:**
```
Step 1: Add searchQuery state variable
Step 2: Bind input to searchQuery with onChange
Step 3: Filter visible content based on search query
Step 4: Or: implement a global search that searches across fields, costs, etc.
```

### 3.2 — Fix Non-Functional Map Overlay Buttons
**File:** `frontend/client/src/components/field/FieldReport.tsx`, Lines ~151–155  
**Fix:**
```
Step 1: Create satellite tile layer toggle (use Leaflet TileLayer switch)
Step 2: NDVI Layer button should overlay NDVI color-coded heatmap from EE data
Step 3: Add onClick handlers with visual feedback (active state styling)
```

### 3.3 — Fix Non-Functional PnL Dashboard Buttons
**File:** `frontend/client/src/components/finance/PnLDashboard.tsx`, Lines ~147–154  
**Fix:**
```
Step 1: Wire "Export" button to ExportButton component (already exists)
Step 2: Wire "Add Entry" to navigate to cost/revenue form
Step 3: Or remove these buttons if not needed
```

### 3.4 — Fix Non-Functional Market Price Search
**File:** `frontend/client/src/components/finance/MarketPrices.tsx`, Lines ~126–131  
**Fix:**
```
Step 1: Add searchTerm state
Step 2: Bind to input onChange
Step 3: Filter rendered market data by searchTerm
```

### 3.5 — Fix Dead Agro Alerts Section
**File:** `frontend/client/src/components/field/Pest.tsx`, Lines ~147–165  
**Fix:**
```
Option A: Implement agro alert fetching from backend (if endpoints exist)
Option B: Remove the empty section entirely
Option C: Mark as "Coming Soon" with appropriate styling
```

### 3.6 — Fix Hardcoded Data Analytics Values
**File:** `frontend/client/src/components/analytics/DataAnalytics.tsx`  
**Fix:**
```
Step 1: Replace ₹2,700 market price with API fetch from /finance/market-prices
Step 2: Replace tree count 0 with actual field data or "Coming Soon" label
Step 3: Replace +2.5% with actual calculation from price history
```

### 3.7 — Fix NDWI Chart Hardcoded Data
**File:** `frontend/client/src/components/analytics/IndicesReport.tsx`, Lines ~85–100  
**Fix:**
```
Step 1: Extract NDWI time-series from the API response data object
Step 2: Map to chart-compatible format
Step 3: Use actual "Current" value from latest data point
```

### 3.8 — Implement Language Persistence
**File:** `frontend/client/src/hooks/useTranslation.tsx`  
**Fix:**
```typescript
// On init:
const [language, setLanguage] = useState<Language>(
  () => (localStorage.getItem('language') as Language) || 'en'
);

// On change:
useEffect(() => {
  localStorage.setItem('language', language);
}, [language]);
```

### 3.9 — Add Language Selector to Dashboard
**File:** `frontend/client/src/pages/Dashboard.tsx` or `TopBar.tsx`  
**Fix:**
```
Step 1: Add a language dropdown in the top bar (near notifications)
Step 2: Use the same LanguageSelector pattern from ChatBot
Step 3: Wire to useTranslation context
```

### 3.10 — Replace All console.error/warn with Logger
**Files:** 61 instances across ~25 files  
**Fix:**
```
Step 1: Find all: console.error, console.warn, console.log in src/ (excluding ui/)
Step 2: Add import { logger } from '@/lib/logger' to each file
Step 3: Replace console.error → logger.error
Step 4: Replace console.warn → logger.warn
Step 5: Replace console.log → logger.info (or remove)

Key files to update:
- FieldContext.tsx (4 instances)
- AuthContext.tsx (2 instances)  
- All planning components (12+ instances)
- All finance components (10+ instances)
- All field components (8+ instances)
- HomeDashboard.tsx (2 instances)
- gemini.ts (4 instances)
- api.ts (1 instance)
```

### 3.11 — Add User-Facing Error Messages (Toast Notifications)
**Files:** All components with catch blocks  
**Fix:**
```
Step 1: Import useToast hook (already available via shadcn)
Step 2: In every catch block that currently only does console.error:
   toast({ title: "Error", description: "Failed to save. Please try again.", variant: "destructive" })
Step 3: Key components to fix:
   - CostCalculator.tsx (cost and revenue submit)
   - All planning components (add/delete/update)
   - FieldContext.tsx (field operations)
   - HomeDashboard.tsx (data loading)
   - ChatBot.tsx (message send)
```

### 3.12 — Fix SignupPage Anti-Pattern (State Update During Render)
**File:** `frontend/client/src/pages/SignupPage.tsx`, Lines 23–25  
**Fix:**
```typescript
// Move redirect into useEffect:
useEffect(() => {
  if (isAuthenticated) setLocation("/dashboard");
}, [isAuthenticated, setLocation]);
```

### 3.13 — Migrate Data Fetching to React Query
**Scope:** All components doing manual useEffect + fetch + useState  
**Fix:**
```
Step 1: Create custom hooks using useQuery for each API endpoint:
   - useFields() → apiGet('/field/')
   - useFieldLogs(fieldId) → apiGet(`/field/${fieldId}/logs`)
   - useCosts(seasonId) → apiGet(`/finance/costs?season=${seasonId}`)
   - useRevenue(seasonId) → apiGet(`/finance/revenue?season=${seasonId}`)
   - useMarketPrices(state) → apiGet(`/finance/market-prices?state=${state}`)
   - usePnLDashboard(fieldId) → apiGet(`/finance/pnl-dashboard?field_id=${fieldId}`)
   - useCalendar(fieldId) → apiGet(`/planning/calendar?field=${fieldId}`)
   - useInventory(fieldId) → apiGet(`/planning/inventory?field=${fieldId}`)
   - useLabor(fieldId) → apiGet(`/planning/labor?field=${fieldId}`)
   - useEquipment(fieldId) → apiGet(`/planning/equipment?field=${fieldId}`)

Step 2: Create mutation hooks using useMutation for write operations

Step 3: Replace manual useState/useEffect patterns in each component

Step 4: Benefits: automatic caching, background refetching, loading/error states,
        request deduplication, optimistic updates
```

### 3.14 — Replace Raw fetch() Calls with apiFetch
**Files:** `FieldContext.tsx`, `AuthContext.tsx`, `MapView.tsx`  
**Fix:** Replace all `fetch()` calls with `apiFetch`/`apiPost`/`apiGet` to get consistent error handling, retry, and timeout.

### 3.15 — Implement Dashboard Deep-Linking
**File:** `frontend/client/src/pages/Dashboard.tsx`  
**Current:** All 20+ dashboard views use `useState('home')` — no URL routing.  
**Fix:**
```
Option A (URL hash): Use wouter hash routing
   /dashboard#pest, /dashboard#finance, /dashboard#planning
   
Option B (URL path): Use wouter nested routes
   /dashboard/pest, /dashboard/finance, /dashboard/planning

Step 1: Replace useState with useLocation from wouter
Step 2: Map URL segments to tab names
Step 3: Update sidebar navigation to use links instead of setState
Step 4: Browser back/forward now works
Step 5: Bookmarkable URLs
```

### 3.16 — Remove Unused Dependencies
**File:** `frontend/package.json`  
**Fix:**
```
Step 1: Remove drizzle-orm (backend ORM, not used in frontend)
Step 2: Remove drizzle-zod (same)
Step 3: Consider if both recharts AND chart.js/react-chartjs-2 are needed
        (standardize on one charting library)
Step 4: Run npm audit fix
```

### 3.17 — Fix Type Safety Issues
**Files:** Multiple  
**Fix:**
```
Step 1: Replace all `any` types with proper interfaces:
   - gemini.ts: Define ChatPayload interface
   - useWeather.ts: Define WeatherResponse, CoordResponse interfaces
   - MapView.tsx: Define FarmPolygon type
   - HomeDashboard.tsx: Define MarketPrice type
   
Step 2: Remove all @ts-ignore suppressions (fix underlying type issues)

Step 3: Add strict mode in tsconfig.json:
   "strict": true,
   "noImplicitAny": true,
   "strictNullChecks": true
```

### 3.18 — Fix Notification Bell Button
**File:** `frontend/client/src/components/layout/TopBar.tsx`, Lines ~44–47  
**Fix:**
```
Step 1: Create a NotificationDropdown component
Step 2: Wire to /field/alerts endpoint
Step 3: Show unread count badge on the bell icon
Step 4: Dropdown shows recent alerts with mark-as-read
```

---

## 6. PHASE 4 — API Design & Data Integrity (Week 3)

### 4.1 — Add URL-Based API Versioning
**File:** `backend/KrishiSaarthi/urls.py`  
**Fix:**
```python
# Current:
path('field/', include('field.urls')),

# Change to:
path('api/v1/field/', include('field.urls')),
path('api/v1/finance/', include('finance.urls')),
path('api/v1/planning/', include('planning.urls')),
path('api/v1/chat/', include('chat.urls')),
path('api/v1/auth/login', Login.as_view()),
path('api/v1/auth/signup', Signup.as_view()),
# etc.
```
Then update all frontend `ENDPOINTS` to match.

### 4.2 — Fix Chat URL Naming
**File:** `backend/chat/urls.py`  
**Current:** `path('a', ...)` — cryptic.  
**Fix:**
```python
urlpatterns = [
    path('', ChatView.as_view(), name='chat_action'),
    path('history/<str:session_id>', ChatHistoryView.as_view(), name='chat_history'),
]
```

### 4.3 — Add Trailing Slashes Consistently
**Files:** All `urls.py` files  
**Fix:** Either add trailing slashes to all URL patterns OR set `APPEND_SLASH = False` in settings. Pick one and be consistent. Django convention is to include them.

### 4.4 — Fix Duplicate /pest Route
**Files:** `backend/KrishiSaarthi/urls.py`, `backend/field/urls.py`  
**Current:** `/pest` at root AND `/field/pest/report` — confusing.  
**Fix:** Remove the root-level `/pest` and keep only `/field/pest/report`.

### 4.5 — Standardize URL Parameter Names
**Files:** `backend/finance/urls.py`  
**Current:** Mix of `<int:pk>`, `<int:scheme_id>`, `<int:claim_id>`.  
**Fix:** Use `<int:pk>` consistently or use `<int:id>` consistently.

### 4.6 — Add Polygon Validation at Model Level
**File:** `backend/field/models.py`  
**Fix:**
```python
from field.validators import validate_polygon

class FieldData(models.Model):
    polygon = models.JSONField(validators=[validate_polygon])
    # ...
```

### 4.7 — Improve Polygon Validator
**File:** `backend/field/validators.py`  
**Fix:**
```
Step 1: Check ring closure (first point == last point)
Step 2: Validate GeoJSON type field ("Polygon")
Step 3: Reject instead of clamping out-of-range coordinates
Step 4: Add maximum area check (e.g., reject polygons > 10,000 hectares)
Step 5: Add self-intersection check using Shapely
```

### 4.8 — Add updated_at to FieldData Model
**File:** `backend/field/models.py`  
**Fix:** `updated_at = models.DateTimeField(auto_now=True)` — then create migration.

### 4.9 — Link Pest Reports to Fields
**File:** `backend/field/models.py`  
**Fix:**
```python
class Pest(models.Model):
    field = models.ForeignKey(FieldData, on_delete=models.SET_NULL, null=True, blank=True, related_name='pest_reports')
    # ...
```

### 4.10 — Add Soft Delete to Key Models
**Files:** `backend/field/models.py`, `backend/finance/models.py`, `backend/planning/models.py`  
**Fix:**
```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

# Add SoftDeleteModel as base for FieldData, FieldLog, CostEntry, Revenue, etc.
# Update all querysets to filter is_deleted=False by default
```

### 4.11 — Add ChatMessage Size Limit
**File:** `backend/chat/models.py`  
**Fix:**
```python
text = models.TextField(max_length=10000)  # Reasonable limit for a chat message
```

### 4.12 — Add Max Chat Sessions Per User
**File:** `backend/chat/views.py`  
**Fix:**
```python
MAX_SESSIONS = 50
if ChatSession.objects.filter(user=request.user).count() >= MAX_SESSIONS:
    # Delete oldest session
    oldest = ChatSession.objects.filter(user=request.user).order_by('created_at').first()
    oldest.delete()
```

---

## 7. PHASE 5 — Performance Optimization (Week 4)

### 5.1 — Offload ML Inference to Celery Workers
**Files:** `backend/field/views/analysis.py` (pest report, health score)  
**Current:** CNN inference runs synchronously in the request handler (~2–5s per request).  
**Fix:**
```
Step 1: Create Celery task: predict_pest_async(image_path, user_id, field_id)
Step 2: In PestReport.post(), save the image and dispatch the task
Step 3: Return 202 Accepted with a task_id
Step 4: Create GET /field/pest/result/<task_id> to poll for results
Step 5: Or: use Django Channels / WebSocket for real-time notification
Step 6: Update frontend to poll or subscribe for results
```

### 5.2 — Batch Celery Tasks
**File:** `backend/field/tasks.py`  
**Fix:**
```
Step 1: Deduplicate fields by location (lat/lng rounded to 2 decimals)
Step 2: Use celery.group() to parallelize API calls:
   from celery import group
   tasks = group(
       fetch_weather.s(lat, lng) for lat, lng in unique_locations
   )
   results = tasks.apply_async()
Step 3: Add rate limiting: max 60 calls/minute for OpenWeather
Step 4: Add retry logic: max_retries=3, countdown=60
Step 5: Cap batch size: process 100 fields per run, use cursor
```

### 5.3 — Add Task Locking (Prevent Concurrent Execution)
**File:** `backend/field/tasks.py`  
**Fix:**
```python
from celery.utils.log import get_task_logger
from django.core.cache import cache

LOCK_EXPIRE = 60 * 30  # 30 minutes

@shared_task(bind=True)
def update_weather_data(self):
    lock_id = 'update-weather-data-lock'
    acquire_lock = cache.add(lock_id, 'locked', LOCK_EXPIRE)
    if not acquire_lock:
        logger.info('Weather update already running, skipping')
        return
    try:
        # ... actual work ...
    finally:
        cache.delete(lock_id)
```

### 5.4 — Batch Earth Engine API Calls
**File:** `backend/field/services/ee_service.py`  
**Current:** 6+ sequential `getInfo()` calls per request.  
**Fix:**
```
Step 1: Combine multiple index computations into a single EE image
Step 2: Use ee.batch.Export for large datasets
Step 3: Cache EE results with field-specific keys (TTL: 24 hours)
Step 4: Consider pre-computing and storing EE data in nightly tasks
```

### 5.5 — Optimize EE Health Check
**File:** `backend/KrishiSaarthi/health.py`  
**Current:** `ee.Initialize()` called on every `/ready` check.  
**Fix:**
```
Step 1: Cache EE initialization status for 5 minutes
Step 2: Only re-initialize if cache expired
Step 3: Or: just check if ee._api_base_url is set (faster)
```

### 5.6 — Add Database Connection Pooling for PostgreSQL
**File:** `backend/KrishiSaarthi/settings.py`  
**Fix:**
```python
# Already has CONN_MAX_AGE=600 for SQLite
# For PostgreSQL, add PgBouncer or use:
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c default_transaction_isolation=read\ committed',
        }
    }
}
# Or add PgBouncer service in docker-compose.prod.yml
```

### 5.7 — Add Endpoint-Specific Throttling for Expensive Operations
**File:** `backend/config/throttling.py` + relevant views  
**Fix:**
```python
class MLInferenceThrottle(UserRateThrottle):
    scope = 'ml_inference'
    rate = '10/hour'

class GeminiChatThrottle(UserRateThrottle):
    scope = 'gemini_chat'
    rate = '30/hour'

class EarthEngineThrottle(UserRateThrottle):
    scope = 'earth_engine'
    rate = '20/hour'

# Apply to specific views:
class PestReport(APIView):
    throttle_classes = [MLInferenceThrottle]
```

### 5.8 — Add Frontend Code Splitting for Heavy Components
**File:** `frontend/vite.config.ts`  
**Fix:**
```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'leaflet': ['leaflet', 'react-leaflet'],
        'charts': ['recharts'],  // or chart.js
        'pdf': ['jspdf', 'jspdf-autotable'],
      }
    }
  }
}
```

### 5.9 — Fix LSTM Temporal Data Issue
**File:** `backend/ml_engine/lstm.py`, `_parse_dict_sequence()` method  
**Current:** Same rainfall/temp/humidity values used for every timestep — temporal weather modeling is ineffective.  
**Fix:**
```
Step 1: Modify the data pipeline to pass actual historical weather per timestep
Step 2: Store weather history alongside NDVI time series
Step 3: Each timestep should have unique [NDVI, rainfall, temp, humidity] values
Step 4: If historical weather unavailable, interpolate or fetch from API
```

### 5.10 — Add React.memo to Expensive Components
**Files:** `HomeDashboard.tsx`, `FieldReport.tsx`, `MapView.tsx`, `ChatBot.tsx`  
**Fix:**
```typescript
export default React.memo(HomeDashboard);
// Or use useMemo for expensive computations within components
```

---

## 8. PHASE 6 — Testing & Quality Assurance (Week 4–5)

### 6.1 — Missing Test Coverage (Priority Order)

| Priority | Endpoint/Feature | Type | Est. Tests |
|----------|-----------------|------|------------|
| **P0** | Password reset flow (request + confirm) | Integration | 5 |
| **P0** | Logout + token deletion | Integration | 2 |
| **P0** | File upload (pest image) with size/type validation | Integration | 4 |
| **P0** | Soil advice input validation | Unit | 3 |
| **P0** | Irrigation schedule calculation | Unit + Integration | 5 |
| **P1** | Yield prediction logic | Unit | 4 |
| **P1** | Carbon credits calculation | Unit | 3 |
| **P1** | EE service circuit breaker | Unit (mocked) | 4 |
| **P1** | Model registry integrity checks | Unit | 3 |
| **P1** | PUT/PATCH for all CRUD endpoints | Integration | 12 |
| **P1** | DELETE for finance endpoints | Integration | 4 |
| **P2** | Pagination on list endpoints | Integration | 5 |
| **P2** | Rate limiting enforcement | Integration | 3 |
| **P2** | Custom exception handler | Unit | 4 |
| **P2** | CORS headers | Integration | 2 |
| **P2** | Edge cases: negative amounts, zero values, huge numbers | Unit | 8 |
| **P2** | Concurrent access (inventory race conditions) | Integration | 3 |
| **P3** | Frontend component tests (React Testing Library) | Component | 15 |
| **P3** | End-to-end flows (Playwright/Cypress) | E2E | 10 |
| | **TOTAL** | | **~99 new tests** |

### 6.2 — Test Quality Improvements
```
Step 1: Add response body assertions to all existing tests
   (don't just check status_code — verify data structure)
Step 2: Add edge case inputs to all CRUD tests:
   - Empty strings, null, undefined
   - Negative numbers, zero, MAX_INT
   - Special characters, SQL injection strings, XSS payloads
   - Very long strings (exceed max_length)
Step 3: Add test for Rabi season fix (month 11, 12, 1, 2, 3)
Step 4: Add test for chat context window (create 30 messages, verify last 20 returned)
Step 5: Mock all external services in tests:
   - @mock.patch for Gemini API
   - @mock.patch for OpenWeather API
   - @mock.patch for Earth Engine
```

### 6.3 — Add Frontend Testing
```
Step 1: Install testing dependencies:
   npm install --save-dev @testing-library/react @testing-library/jest-dom
   npm install --save-dev vitest @testing-library/user-event
   npm install --save-dev msw (Mock Service Worker for API mocking)

Step 2: Create test setup file (src/test/setup.ts)

Step 3: Write tests for critical flows:
   - Login form validation and submission
   - Signup form with validation
   - Dashboard tab navigation
   - Field creation with polygon drawing
   - Chat message send and receive
   - Financial data entry (cost, revenue)

Step 4: Add to vite.config.ts:
   test: {
     environment: 'jsdom',
     setupFiles: ['./src/test/setup.ts'],
   }
```

### 6.4 — Add Code Quality Tools

**Backend (Python):**
```
Step 1: pip install flake8 black isort mypy
Step 2: Create pyproject.toml:
   [tool.black]
   line-length = 120
   
   [tool.isort]
   profile = "black"
   
   [tool.mypy]
   python_version = "3.11"
   warn_return_any = true
   warn_unused_configs = true

Step 3: Add pre-commit hook:
   pip install pre-commit
   Create .pre-commit-config.yaml with black, isort, flake8

Step 4: Run once: black . && isort . && flake8 .
```

**Frontend (TypeScript):**
```
Step 1: npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
Step 2: npm install --save-dev prettier eslint-config-prettier
Step 3: Create .eslintrc.cjs with strict TypeScript rules
Step 4: Create .prettierrc
Step 5: Add scripts to package.json:
   "lint": "eslint src/ --ext .ts,.tsx",
   "format": "prettier --write src/"
```

---

## 9. PHASE 7 — DevOps & CI/CD Pipeline (Week 5–6)

### 7.1 — Create GitHub Actions CI Pipeline
**File:** `.github/workflows/ci.yml`
```yaml
name: CI
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_krishisaarthi
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
        ports: ['5432:5432']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -m pytest tests/ -v --tb=short
      
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install flake8 black isort
      - run: cd backend && black --check . && isort --check .
      
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci
      - run: cd frontend && npm run check  # TypeScript check
      - run: cd frontend && npm run build
      
  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run lint

  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose -f docker-compose.yml build
      
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install safety && safety check -r backend/requirements.txt
      - run: cd frontend && npm audit --production
```

### 7.2 — Create CD Pipeline for Staging/Production
**File:** `.github/workflows/deploy.yml`
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy-staging:
    # ... build, push to registry, deploy to staging
  deploy-production:
    needs: deploy-staging
    environment: production  # Requires manual approval
    # ... deploy to production
```

### 7.3 — Create .dockerignore
**File:** `backend/.dockerignore`
```
__pycache__/
*.pyc
*.pyo
.git/
.gitignore
db.sqlite3
venv/
.env
*.log
tests/
.pytest_cache/
node_modules/
```

### 7.4 — Multi-Stage Docker Build
**File:** `backend/Dockerfile`
```dockerfile
# Stage 1: Build dependencies (has gcc, g++)
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y gcc g++ libgdal-dev
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (no build tools)
FROM python:3.11-slim
RUN apt-get update && apt-get install -y libgdal32 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . /app
WORKDIR /app
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "KrishiSaarthi.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 7.5 — Add Database Migration to Production Entrypoint
**File:** `backend/entrypoint.sh` (new)  
```bash
#!/bin/bash
set -e
echo "Running migrations..."
python manage.py migrate --noinput
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Starting Gunicorn..."
exec gunicorn KrishiSaarthi.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120
```

### 7.6 — Fix Redis Health Check in Production
**File:** `docker-compose.prod.yml`  
**Fix:**
```yaml
redis:
  healthcheck:
    test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
```

### 7.7 — Consolidate Docker Builds (Single Image for Backend)
**File:** `docker-compose.prod.yml`  
**Fix:**
```yaml
backend:
  build: ./backend
  image: krishisaarthi-backend:latest
  
celery-worker:
  image: krishisaarthi-backend:latest  # Same image, different command
  command: celery -A KrishiSaarthi worker -l info
  
celery-beat:
  image: krishisaarthi-backend:latest  # Same image, different command
  command: celery -A KrishiSaarthi beat -l info
```

### 7.8 — Create .env.example Files
**File:** `.env.example` (project root)
```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here-change-me
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://krishiuser:password@db:5432/krishisaarthi
POSTGRES_DB=krishisaarthi
POSTGRES_USER=krishiuser
POSTGRES_PASSWORD=change-this-strong-password

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=change-this-strong-password

# External APIs
GEMINI_API_KEY=your-gemini-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Google Earth Engine
GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Encryption
FERNET_KEY=your-fernet-encryption-key

# Monitoring
GRAFANA_PASSWORD=change-this-strong-password
```

### 7.9 — Add SSL Certificate Automation
**Fix:**
```
Option A: Certbot with Let's Encrypt
Step 1: Add certbot service to docker-compose.prod.yml
Step 2: Generate initial certs with standalone mode
Step 3: Add renewal cron job (certbot renew every 12 hours)
Step 4: Mount certs into nginx container

Option B: Cloudflare proxy (easier)
Step 1: Set up Cloudflare DNS
Step 2: Enable "Full (strict)" SSL mode
Step 3: Cloudflare handles cert provisioning and renewal
```

### 7.10 — Add .gitignore Improvements
**File:** `.gitignore`
```
# Database
backend/db.sqlite3

# Environment
.env
*.env.local

# Python
__pycache__/
*.pyc
*.pyo
venv/
.pytest_cache/

# Node
node_modules/
dist/

# Logs
*.log
backend/logs/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Docker volumes
postgres_data/
```

---

## 10. PHASE 8 — Monitoring & Observability (Week 6)

### 8.1 — Install Django Prometheus Metrics
```
Step 1: pip install django-prometheus
Step 2: Add 'django_prometheus' to INSTALLED_APPS
Step 3: Add middleware:
   'django_prometheus.middleware.PrometheusBeforeMiddleware' (first)
   'django_prometheus.middleware.PrometheusAfterMiddleware' (last)
Step 4: Add URL:
   path('prometheus/', include('django_prometheus.urls'))
Step 5: Replace 'django.db.backends.sqlite3' with 
   'django_prometheus.db.backends.sqlite3' (or postgresql)
```

### 8.2 — Add Custom Application Metrics
**File:** `backend/config/metrics.py` (new)
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'Request duration', ['endpoint'])

# ML metrics
ml_predictions_total = Counter('ml_predictions_total', 'ML predictions', ['model', 'result'])
ml_prediction_duration = Histogram('ml_prediction_duration_seconds', 'ML inference time', ['model'])
ml_predictions_failed = Counter('ml_predictions_failed_total', 'Failed predictions', ['model'])

# Business metrics
active_users_gauge = Gauge('active_users', 'Currently active users')
fields_total = Gauge('fields_total', 'Total fields in system')
chat_messages_total = Counter('chat_messages_total', 'Chat messages sent')

# External API metrics
external_api_calls = Counter('external_api_calls_total', 'External API calls', ['service', 'status'])
external_api_duration = Histogram('external_api_duration_seconds', 'External API latency', ['service'])
```

### 8.3 — Add Missing Prometheus Exporters to Docker Compose
**File:** `docker-compose.prod.yml`
```yaml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  environment:
    DATA_SOURCE_NAME: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}?sslmode=disable"
  depends_on: [db]
  networks: [krishisaarthi-network]

redis-exporter:
  image: oliver006/redis_exporter:latest
  environment:
    REDIS_ADDR: "redis://redis:6379"
    REDIS_PASSWORD: "${REDIS_PASSWORD}"
  depends_on: [redis]
  networks: [krishisaarthi-network]

node-exporter:
  image: prom/node-exporter:latest
  volumes:
    - /proc:/host/proc:ro
    - /sys:/host/sys:ro
  networks: [krishisaarthi-network]
```

### 8.4 — Configure Alertmanager
**File:** `monitoring/alertmanager.yml` (new)
```yaml
global:
  smtp_from: 'alerts@yourdomain.com'
  smtp_smarthost: 'smtp.gmail.com:587'
route:
  group_by: ['alertname']
  receiver: 'team-email'
receivers:
  - name: 'team-email'
    email_configs:
      - to: 'team@yourdomain.com'
        send_resolved: true
```

### 8.5 — Fix Alert Rules to Match Actual Metrics
**File:** `monitoring/alerts.yml`
```
Step 1: Update metric names to match django-prometheus output:
   http_requests_total → django_http_requests_total_by_method_total
   http_request_duration_seconds → django_http_requests_latency_seconds
Step 2: Add meaningful alerts:
   - API error rate > 5% for 5 minutes
   - Response latency p95 > 2s for 5 minutes
   - Database connection pool exhausted
   - Redis connection failures
   - Celery queue depth > 100 tasks
   - ML model file missing/corrupt
   - Disk usage > 80%
```

### 8.6 — Fix Grafana Dashboard Panels
**File:** `monitoring/grafana/dashboards/`
```
Step 1: Update all panel queries to match actual prometheus metric names
Step 2: Add panels for:
   - Request rate by endpoint
   - Error rate by endpoint
   - P50/P95/P99 latency
   - Active database connections
   - Redis hit/miss ratio
   - Celery task queue depth
   - Celery task success/failure rate
   - ML inference latency and throughput
   - External API call latency (Gemini, OpenWeather, EE)
```

### 8.7 — Add Structured JSON Logging
**File:** `backend/config/logging_config.py`
```
Step 1: pip install python-json-logger
Step 2: Configure JSON formatter:
   'json': {
       'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
       'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
   }
Step 3: Add loggers for ALL modules:
   'chat', 'finance', 'planning', 'middleware', 'ml_engine'
Step 4: In production, use JSON formatter for all file handlers
Step 5: Consider forwarding to ELK stack or Datadog
```

### 8.8 — Exclude Health Checks from Request Logging
**File:** `backend/middleware/request_logging.py`
```python
EXCLUDED_PATHS = ['/health', '/ready', '/prometheus/']

def __call__(self, request):
    if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
        return self.get_response(request)
    # ... normal logging ...
```

---

## 11. PHASE 9 — ML Engine Hardening (Week 7)

### 9.1 — Add Model A/B Testing Support
**File:** `backend/ml_engine/registry.py`
```
Step 1: Add model_variant field to registry (e.g., "control" vs "candidate")
Step 2: Add prediction logging (model used, input hash, output, latency)
Step 3: Create admin dashboard to compare model performance
Step 4: Enable gradual rollout: 90% traffic to control, 10% to candidate
```

### 9.2 — Add Batch Inference Support for CNN
**File:** `backend/ml_engine/cnn.py`
```python
def predict_health_batch(image_paths: list[str]) -> list[dict]:
    """Batch inference for multiple images"""
    model = get_model()
    if model is None:
        return [_fallback_result() for _ in image_paths]
    
    tensors = [_preprocess(path) for path in image_paths]
    batch = torch.stack(tensors)
    with torch.no_grad():
        outputs = model(batch)
    return [_format_result(o) for o in outputs]
```

### 9.3 — Add Model Retraining Pipeline
```
Step 1: Create data collection pipeline:
   - Log all pest predictions with user feedback (correct/incorrect)
   - Store labeled images in a training dataset folder
   
Step 2: Create retraining script:
   - Fine-tune MobileNetV2 on accumulated labeled data
   - Validate on held-out test set
   - Only promote if accuracy improves

Step 3: Create management command:
   python manage.py retrain_pest_model --min-samples=1000
   
Step 4: Add model performance monitoring:
   - Track prediction confidence distribution over time
   - Alert if average confidence drops (data drift)
```

### 9.4 — Add Data Privacy Notice for Gemini Uploads
**File:** `backend/field/views/analysis.py`, `_validate_plant_image()`  
**Current:** User crop images are sent to Google Gemini with no consent or notice.  
**Fix:**
```
Step 1: Add clear notice on the frontend pest detection page:
   "Your crop images will be analyzed using Google's AI service for 
    pest detection. Images are processed in real-time and not stored 
    by Google."
Step 2: Add user consent checkbox before first upload
Step 3: Store consent timestamp in user profile
Step 4: Log all external API data transmissions for compliance
```

### 9.5 — Fix Gemini Fail-Open to Fail-Closed
**File:** `backend/field/views/analysis.py`, Lines ~127–128  
**Current:** If Gemini validation fails, the image is treated as a valid plant image.  
**Fix:**
```python
# Change from fail-open to fail-closed:
except Exception as e:
    logger.error("Image validation failed: %s", str(e))
    return Response({
        'error': 'Unable to validate image. Please try again.',
        'retry': True
    }, status=503)
```

### 9.6 — Add GPU Memory Management
**File:** `backend/ml_engine/cnn.py`, `backend/ml_engine/lstm.py`
```python
import gc
def predict_health(image_path):
    try:
        result = _run_inference(image_path)
        return result
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
```

---

## 12. PHASE 10 — Production Deployment Checklist (Week 7–8)

### Pre-Deployment Checklist

- [ ] **Environment Variables** — All secrets in `.env`, no defaults for production
- [ ] **DEBUG=False** — Verified not leaking stack traces
- [ ] **SECRET_KEY** — Unique, random 50+ character key
- [ ] **ALLOWED_HOSTS** — Set to actual domain names only
- [ ] **CORS_ALLOWED_ORIGINS** — Set to actual frontend domain only
- [ ] **Database** — PostgreSQL (not SQLite) with strong password
- [ ] **SSL/TLS** — Valid certificates installed and auto-renewing
- [ ] **HSTS** — Enabled with minimum 1 year max-age
- [ ] **Database Migrations** — Run successfully in production
- [ ] **Static Files** — Collected and served by Nginx (not Django)
- [ ] **Media Files** — Stored on persistent volume with backup
- [ ] **ML Models** — Files present and integrity verified
- [ ] **Celery Workers** — Running and processing tasks
- [ ] **Redis** — Running with authentication enabled
- [ ] **Prometheus** — Scraping all targets successfully
- [ ] **Grafana** — Dashboards loading with real data
- [ ] **Alertmanager** — Test alert received via email
- [ ] **Backups** — Database backup cron job configured
- [ ] **Log Rotation** — Configured to prevent disk full
- [ ] **Health Checks** — All services passing `/health` and `/ready`
- [ ] **Rate Limiting** — Tested and working
- [ ] **Error Handling** — No stack traces leak to users
- [ ] **Token Expiry** — Tokens expire after 24 hours
- [ ] **Password Policy** — Minimum 8 chars, complexity validated

### Nginx Production Hardening

```
Step 1: Fix add_header inheritance issue:
   Move all security headers to an include file
   Include it in EVERY location block

Step 2: Add Content-Security-Policy header:
   Content-Security-Policy: default-src 'self'; 
     script-src 'self'; style-src 'self' 'unsafe-inline';
     img-src 'self' data: blob: https://*.tile.openstreetmap.org;
     connect-src 'self' https://generativelanguage.googleapis.com;

Step 3: Add OCSP stapling:
   ssl_stapling on;
   ssl_stapling_verify on;

Step 4: Add WebSocket support (if needed for chat):
   location /ws/ {
     proxy_http_version 1.1;
     proxy_set_header Upgrade $http_upgrade;
     proxy_set_header Connection "upgrade";
   }
```

### Database Backup Strategy
```
Step 1: Create backup script:
   pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > backup_$(date +%Y%m%d).sql.gz

Step 2: Schedule daily backup via cron or Celery beat

Step 3: Store backups in:
   - Local volume (7 days retention)
   - Cloud storage (90 days retention: S3, GCS, etc.)

Step 4: Test restore procedure monthly:
   gunzip < backup.sql.gz | psql -U $POSTGRES_USER $POSTGRES_DB
```

### Disaster Recovery Plan
```
Step 1: Document:
   - How to restore database from backup
   - How to redeploy from a specific Git commit
   - How to rotate compromised secrets
   - Contact list for emergencies

Step 2: Set RTO (Recovery Time Objective): 4 hours
Step 3: Set RPO (Recovery Point Objective): 24 hours (daily backups)
Step 4: Practice recovery drill quarterly
```

---

## 13. PHASE 11 — Customer-Readiness & Polish (Week 8–9)

### 11.1 — Complete i18n Coverage
```
Step 1: Audit ALL user-facing strings in the frontend
Step 2: Add translation keys for:
   - Dashboard sidebar labels (20+ items)
   - All page headers and section titles
   - All button labels
   - All form labels and placeholders
   - All error messages
   - All success messages
   - All empty state messages
   - Date/number formatting per locale

Step 3: Get professional translations for Hindi, Punjabi, Malayalam
Step 4: Add language selector in main navigation (not just ChatBot)
Step 5: Persist language choice in localStorage
Step 6: Consider adding:
   - Tamil, Telugu, Kannada, Bengali, Marathi (major farming languages)
   - RTL support for Urdu if needed
```

### 11.2 — Accessibility Compliance (WCAG 2.1 AA)
```
Step 1: Add aria-labels to ALL interactive elements:
   - Sidebar navigation buttons
   - Mobile hamburger menu
   - Search inputs
   - Map toolbar buttons
   - Notification bell
   - Close buttons
   - Tab controls

Step 2: Bind <label> to inputs via htmlFor/id:
   - Login form
   - Signup form
   - All financial forms
   - All planning forms

Step 3: Add keyboard navigation:
   - Tab order through dashboard sidebar
   - Enter to activate buttons
   - Escape to close modals/dropdowns
   - Arrow keys for tab navigation

Step 4: Color contrast:
   - Verify all text meets 4.5:1 contrast ratio
   - Don't rely solely on color to convey information
   - Add patterns/icons alongside color indicators

Step 5: Screen reader support:
   - Add role attributes to custom containers
   - Announce dynamic content changes via aria-live regions
   - Provide text alternatives for charts and maps

Step 6: Test with:
   - NVDA/JAWS screen reader
   - axe DevTools browser extension
   - Lighthouse accessibility audit
```

### 11.3 — User Onboarding Flow
```
Step 1: First-login tutorial:
   - Welcome modal explaining key features
   - Step-by-step guide to create first field
   - Tooltip hints on important buttons

Step 2: Empty states:
   - When no fields exist: show "Create your first field" CTA
   - When no costs/revenue: show "Start tracking your expenses" CTA
   - When no chat history: show suggested questions

Step 3: Sample data option:
   - "Load sample data" button for demo purposes
   - Pre-populated field, costs, revenue for exploration
```

### 11.4 — Offline Support (Progressive Enhancement)
```
Step 1: Add service worker for static asset caching
Step 2: Cache recently viewed field data in IndexedDB
Step 3: Queue form submissions when offline
Step 4: Sync when connection restored
Step 5: Show offline indicator in UI
```

### 11.5 — Print / PDF Export
```
Step 1: Wire up PnL Dashboard "Export" button to jsPDF
Step 2: Add export functionality for:
   - Field reports (NDVI history, health scores)
   - Financial summaries (season P&L)
   - Pest detection reports
   - Carbon credit certificates

Step 3: Use jsPDF + jspdf-autotable (already installed)
Step 4: Add print-friendly CSS (@media print)
```

### 11.6 — Performance Budget
```
Set and enforce limits:
   - First Contentful Paint: < 1.5s
   - Largest Contentful Paint: < 2.5s
   - Time to Interactive: < 3.0s
   - Total JS bundle: < 500KB (gzip)
   - API response time (p95): < 500ms (non-ML endpoints)
   - API response time (p95): < 5s (ML inference endpoints)

Measure with:
   - Lighthouse CI in GitHub Actions
   - Web Vitals reporting to analytics
```

### 11.7 — Legal & Compliance
```
Step 1: Add Privacy Policy page
   - What data is collected
   - How it's used
   - Third-party services (Google Gemini, Earth Engine, OpenWeather)
   - Data retention period
   - User rights (access, delete, export)

Step 2: Add Terms of Service page

Step 3: Add Cookie consent banner (if applicable)

Step 4: Implement data export (GDPR Article 20):
   - "Download my data" button in user settings
   - Export as JSON/CSV

Step 5: Implement account deletion:
   - "Delete my account" in settings
   - Cascade delete all user data
   - Send confirmation email
   
Step 6: Add data processing agreement for Gemini API usage
```

---

## 14. PHASE 12 — Documentation & Handoff (Week 9–10)

### 12.1 — API Documentation
```
Step 1: Install drf-spectacular:
   pip install drf-spectacular
   
Step 2: Add to INSTALLED_APPS and REST_FRAMEWORK:
   'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema'

Step 3: Add URL:
   path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
   path('api/docs/', SpectacularSwaggerView.as_view(), name='swagger-ui'),

Step 4: Annotate views with @extend_schema for parameters, responses, examples

Step 5: Result: Interactive API documentation at /api/docs/
```

### 12.2 — Deployment Guide
```
Create docs/DEPLOYMENT.md with:
   1. Server requirements (CPU, RAM, disk)
   2. Domain and DNS setup
   3. SSL certificate provisioning
   4. Environment variable configuration
   5. Docker setup step-by-step
   6. Database initialization
   7. First admin user creation
   8. EE service account setup
   9. Monitoring verification
   10. Backup configuration
   11. Rollback procedures
   12. Scaling guide (horizontal, vertical)
```

### 12.3 — User Manual
```
Create docs/USER_GUIDE.md (or in-app help) with:
   1. Getting started (signup, first field)
   2. Field management (drawing boundaries, viewing data)
   3. Pest detection (uploading images)
   4. Financial tracking (costs, revenue, P&L)
   5. Planning tools (calendar, inventory, labor, equipment)
   6. AI chatbot usage
   7. Analytics and reports
   8. Settings and preferences
   9. FAQ
```

### 12.4 — Developer Guide
```
Create docs/DEVELOPMENT.md with:
   1. Local development setup
   2. Project architecture overview
   3. Adding a new API endpoint
   4. Adding a new ML model
   5. Adding a new frontend page
   6. Running tests
   7. Code style guide
   8. Git branch strategy
   9. PR review process
   10. Release process
```

### 12.5 — Architecture Decision Records (ADRs)
```
Create docs/adr/ directory with:
   ADR-001: Why wouter instead of react-router
   ADR-002: Why Django REST Framework over FastAPI
   ADR-003: Why MobileNetV2 for pest detection
   ADR-004: Why Token auth instead of JWT
   ADR-005: Why React Query + Context instead of Redux
   ADR-006: Why Earth Engine instead of Sentinel Hub
```

---

## 15. Full Issue Tracker

### By Severity

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical** | 14 | Security vulnerabilities, data loss risks, deployment blockers |
| **High** | 25 | Functional bugs, missing validation, broken features |
| **Medium** | 38 | Code quality, performance, UX issues |
| **Low** | 18 | Style, naming, minor improvements |
| **Enhancement** | 52 | New capabilities for production readiness |
| **Total** | **147** |

### By Category

| Category | Critical | High | Medium | Low | Enhancement | Total |
|----------|----------|------|--------|-----|-------------|-------|
| Security & Auth | 6 | 3 | 2 | 0 | 3 | 14 |
| Backend Logic Bugs | 1 | 5 | 4 | 3 | 0 | 13 |
| Input Validation | 0 | 4 | 3 | 0 | 2 | 9 |
| Frontend UI/UX | 0 | 4 | 6 | 3 | 8 | 21 |
| Frontend Code Quality | 0 | 1 | 5 | 3 | 4 | 13 |
| API Design | 0 | 1 | 3 | 3 | 3 | 10 |
| Data Integrity | 1 | 3 | 2 | 2 | 2 | 10 |
| Testing | 0 | 2 | 2 | 0 | 6 | 10 |
| DevOps/CI/CD | 4 | 2 | 1 | 1 | 8 | 16 |
| Monitoring | 2 | 0 | 2 | 0 | 5 | 9 |
| ML Engine | 0 | 0 | 3 | 1 | 5 | 9 |
| Performance | 0 | 0 | 3 | 1 | 4 | 8 |
| i18n/A11y | 0 | 0 | 2 | 1 | 2 | 5 |

---

## 16. Architecture Recommendations

### Current Architecture
```
[React SPA] → [Nginx] → [Django + DRF + Gunicorn]
                              ↓          ↓         ↓
                         [PostgreSQL]  [Redis]  [Celery Workers]
                                                    ↓
                                          [External APIs: Gemini, EE, OpenWeather]
                                          [ML Models: CNN, LSTM]
```

### Recommended Architecture (Production)
```
[CloudFront CDN]
      ↓
[React SPA (S3/Nginx)]
      ↓
[Application Load Balancer]
      ↓
[Nginx (SSL + Rate Limit + Security Headers)]
      ↓
[Django + DRF + Gunicorn × 4 workers]
    ↓           ↓           ↓            ↓
[PostgreSQL]  [Redis     [Celery     [ML Inference
 (Primary     (Cache +    Workers     Service
  + Replica)]  Queue)]    × 2-4)]   (separate)]
                             ↓
                [External APIs with circuit breakers]
                     ↓           ↓            ↓
              [Google EE]  [Gemini AI]  [OpenWeather]

[Prometheus + Grafana + Alertmanager] → [monitoring]
[Loki / ELK] → [centralized logging]
[S3/GCS] → [backups, media storage]
```

### Scaling Strategy
```
Phase 1 (< 100 users): Current single-server Docker Compose
Phase 2 (100-1000 users): 
   - Add PostgreSQL read replica
   - Increase Celery workers to 4
   - Separate ML inference to dedicated service
   - Add CDN for static assets
Phase 3 (1000-10000 users):
   - Kubernetes deployment
   - Horizontal pod autoscaling
   - PgBouncer for connection pooling
   - Redis Cluster
   - Async ML via separate GPU service
Phase 4 (10000+ users):
   - Multi-region deployment
   - Database sharding by user region
   - Edge caching for satellite data
   - Dedicated ML inference cluster
```

---

## Timeline Summary

| Week | Phase | Focus | Effort |
|------|-------|-------|--------|
| 1 | Phase 1 | Critical Security Fixes | 40 hours |
| 2 | Phase 2 | Backend Bug Fixes & Validation | 35 hours |
| 2–3 | Phase 3 | Frontend Fixes & UX | 45 hours |
| 3 | Phase 4 | API Design & Data Integrity | 25 hours |
| 4 | Phase 5 | Performance Optimization | 30 hours |
| 4–5 | Phase 6 | Testing & QA | 40 hours |
| 5–6 | Phase 7 | DevOps & CI/CD | 35 hours |
| 6 | Phase 8 | Monitoring & Observability | 25 hours |
| 7 | Phase 9 | ML Engine Hardening | 20 hours |
| 7–8 | Phase 10 | Production Deployment | 20 hours |
| 8–9 | Phase 11 | Customer Polish | 35 hours |
| 9–10 | Phase 12 | Documentation | 20 hours |
| | | **TOTAL** | **~370 hours** |

---

## Priority Summary: What to Do First

### This Week (Critical — Must Fix)
1. Token expiry implementation
2. Bank account encryption
3. Password reset security (user enumeration + validation)
4. Login timing side-channel fix
5. Docker password defaults
6. Remove source mount in production compose
7. Global 401 interceptor in frontend

### Next Week (High — Should Fix)
8. Rabi season logic bug
9. Chat context window (last 20, not first 20)
10. Irrigation fallback coordinates error
11. Insurance claims serializer
12. All non-functional UI elements
13. Pagination on all list endpoints
14. Weather/risk tasks actually storing data

### Following Weeks (Medium — Improve)
15. React Query migration
16. console.error → logger replacement (all 61 instances)
17. Toast notifications for user-facing errors
18. CI/CD pipeline setup
19. Monitoring stack (working Prometheus/Grafana)
20. Test coverage expansion (99 new tests)

---

*End of Report. Total findings: 147 items across 12 phases. Estimated effort: ~370 hours to production-ready.*
