# Comprehensive Codebase Audit Report

**Generated:** June 2025  
**Scope:** All files NOT previously fixed  

---

## Category 1: Backend Views

### 1.1 — `rotation.py` season logic bug (always-False condition)
- **File:** `backend/planning/views/rotation.py`, **Lines 166–169**
- **Problem:** `elif 11 <= month <= 3` is **always False** — no integer can be simultaneously ≥ 11 and ≤ 3. The Rabi season is never returned; execution falls through to the `else` (Zaid) for months Nov–Mar.
- **Severity:** **Critical**
- **Fix:** Split into `elif month >= 11 or month <= 3:`

### 1.2 — `irrigation.py` hardcoded fallback coordinates
- **File:** `backend/field/views/irrigation.py`, **~Line 114**
- **Problem:** When a field has no stored lat/lng the code silently falls back to `lat, lng = 10.0, 76.0` (a location in Kerala). Users in other states get completely wrong weather-based irrigation recommendations with no warning.
- **Severity:** **High**
- **Fix:** Return an error response telling the user to save their field location instead of silently using a Kerala default.

### 1.3 — `irrigation.py` uses `datetime.now()` instead of timezone-aware `timezone.now()`
- **File:** `backend/field/views/irrigation.py`, **~Line 148**
- **Problem:** `datetime.now()` returns a naive datetime. If `USE_TZ=True` in Django settings, this can cause comparison/runtime warnings and subtle date-boundary bugs.
- **Severity:** **Medium**
- **Fix:** Use `from django.utils import timezone; timezone.now()`

### 1.4 — `schemes.py` auto-seed race condition
- **File:** `backend/finance/views/schemes.py`, **Lines ~157–158**
- **Problem:** `if not GovernmentScheme.objects.exists(): self._seed_schemes()` — two concurrent requests can both see an empty table and both attempt seeding, creating duplicate rows.
- **Severity:** **High**
- **Fix:** Wrap in `select_for_update()` or use a migration / management command to seed, not a runtime check.

### 1.5 — `insurance.py` manual field validation bypasses serializer
- **File:** `backend/finance/views/insurance.py`, **Lines ~107–113**
- **Problem:** POST handler validates fields manually (`if not crop: …`) instead of using a DRF serializer. This is error-prone and inconsistent with the rest of the codebase.
- **Severity:** **Medium**
- **Fix:** Define and use an `InsuranceClaimSerializer` with proper field validation.

### 1.6 — `insurance.py` stores `bank_account` and `ifsc_code` as plaintext
- **File:** `backend/finance/views/insurance.py` + `backend/finance/models.py`
- **Problem:** Sensitive financial data (bank account number, IFSC code) is stored as plain `CharField` with no encryption or masking.
- **Severity:** **High**
- **Fix:** Encrypt at rest using `django-fernet-fields` or similar. At minimum mask the account number in API responses.

### 1.7 — `price_forecast.py` unvalidated `int()` cast
- **File:** `backend/finance/views/price_forecast.py`, **~Line 76**
- **Problem:** `days = int(request.query_params.get('days', 30))` will throw `ValueError` if a non-integer string is passed, resulting in an unhandled 500 error.
- **Severity:** **Medium**
- **Fix:** Wrap in try/except and return `400 Bad Request` on invalid input.

### 1.8 — `pnl_dashboard.py` has no error handling
- **File:** `backend/finance/views/pnl_dashboard.py`, full file
- **Problem:** No try/except anywhere in the view. Any exception (e.g., missing data, DB error) returns a raw 500 to the client.
- **Severity:** **Medium**
- **Fix:** Add try/except with proper error responses.

### 1.9 — `soil_advice.py` no range validation on N/P/K values
- **File:** `backend/field/views/soil_advice.py`
- **Problem:** User-supplied N, P, K values are passed directly to the Gemini prompt without checking for negative, zero, or absurdly large values.
- **Severity:** **Low**
- **Fix:** Validate ranges (e.g., 0–1000 ppm) before calling the external API.

### 1.10 — Multiple finance/planning views return 200 on DELETE
- **Files:** `cost_calculator.py` ~L82, `revenue.py` ~L67, `season.py` ~L80, all planning DELETE handlers
- **Problem:** DELETE endpoints return `status=200` with a message body instead of the RESTful `204 No Content`.
- **Severity:** **Low**
- **Fix:** Return `Response(status=status.HTTP_204_NO_CONTENT)`.

### 1.11 — `market_prices.py` uses bare `500` status int
- **File:** `backend/finance/views/market_prices.py`, **~Line 107**
- **Problem:** `return Response(…, status=500)` instead of `status=status.HTTP_500_INTERNAL_SERVER_ERROR`. Inconsistent with DRF conventions and harder to grep.
- **Severity:** **Low**
- **Fix:** Use `status.HTTP_500_INTERNAL_SERVER_ERROR`.

### 1.12 — `chat/views.py` fetches first 20 messages, not last 20
- **File:** `backend/chat/views.py`, **Line 63**
- **Problem:** `session.messages.all().order_by('timestamp')[:20]` slices the **first** 20 messages chronologically. In a long conversation the most recent context is lost.
- **Severity:** **High**
- **Fix:** Use `.order_by('-timestamp')[:20]` then reverse the list, or use `.order_by('timestamp')[count-20:]`.

### 1.13 — `field_crud.py` camelCase class name `getCoord`
- **File:** `backend/field/views/field_crud.py`, **~Line 105**
- **Problem:** Python class name `getCoord` violates PEP 8 (should be `GetCoord`).
- **Severity:** **Low**
- **Fix:** Rename to `GetCoord` (also update `urls.py`).

---

## Category 2: Backend Serializers

### 2.1 — Password `min_length` validation bypassed in Signup
- **File:** `backend/KrishiSaarthi/serializers.py`, **Line 9** + `backend/KrishiSaarthi/views.py`, **Lines 42–47**
- **Problem:** The `UserSerializer` defines `password = serializers.CharField(…, min_length=8)` but the `Signup` view calls `user.set_password(request.data['password'])` directly from `request.data`, bypassing serializer validation for the password field since `serializer.save()` already saved a hashed password from the serializer.
- **Severity:** **High**
- **Fix:** Either do password setting inside the serializer's `create()` method, or remove the duplicate save. Currently the user is saved once with the serializer (which hashes the password already if `create()` calls `set_password`), then fetched again and `set_password` is called a second time — double save, double hash.

---

## Category 3: Backend Models

### 3.1 — `field/models.py` uses camelCase `cropType`
- **File:** `backend/field/models.py`
- **Problem:** `cropType = models.CharField(…)` uses camelCase instead of Django's `snake_case` convention (`crop_type`).
- **Severity:** **Low**
- **Fix:** Rename to `crop_type` and run a migration. (Breaking change — coordinate with frontend.)

### 3.2 — `finance/models.py` `InsuranceClaim.bank_account` stored unencrypted
- **File:** `backend/finance/models.py`
- **Problem:** Sensitive PII field stored as plain `CharField`. (Duplicate of 1.6 — model layer.)
- **Severity:** **High**
- **Fix:** See 1.6.

### 3.3 — `planning/models.py` allows negative inventory
- **File:** `backend/planning/models.py`, **~Line 137**
- **Problem:** `InventoryTransaction.save()` uses `F('quantity') - self.quantity` for "use" transactions but does not enforce `quantity >= 0` at the DB level. A race condition or large deduction could make stock negative.
- **Severity:** **Medium**
- **Fix:** Add a `CheckConstraint` on `InventoryItem.quantity >= 0` and/or use `select_for_update()`.

### 3.4 — `planning/models.py` `LaborEntry.save()` total_wage=0 edge case
- **File:** `backend/planning/models.py`
- **Problem:** Auto-calculates `total_wage` only when `total_wage is None`. If `total_wage=0` is explicitly passed it won't be recalculated, even though `hours_worked * hourly_rate` might be non-zero.
- **Severity:** **Low**
- **Fix:** Change condition to `if not self.total_wage:` or always recalculate.

### 3.5 — `finance/models.py` `Revenue.total_amount` similar edge case
- **File:** `backend/finance/models.py`, **~Line 100**
- **Problem:** Same pattern — only auto-calculates when `total_amount is None`, not when 0.
- **Severity:** **Low**
- **Fix:** Always recalculate, or check `if self.total_amount in (None, 0):`.

---

## Category 4: Frontend AuthContext

### 4.1 — No server-side token validation on mount
- **File:** `frontend/client/src/context/AuthContext.tsx`, **Lines 66–76**
- **Problem:** On page load, the app trusts a token from `localStorage` without verifying it's still valid server-side. An expired or revoked token lets the user appear logged in until the first API call fails.
- **Severity:** **Critical**
- **Fix:** Call `/test_token` on mount. If it fails, clear auth state and redirect to login.

### 4.2 — Logout doesn't invalidate server-side token
- **File:** `frontend/client/src/context/AuthContext.tsx`, **Lines 39–44**
- **Problem:** `logout()` only clears local state. The Django token remains valid in the DB. If stolen, it can still be used.
- **Severity:** **High**
- **Fix:** Send a `POST /logout` request to delete the token server-side before clearing local state.

### 4.3 — `console.error` calls in login/signup
- **File:** `frontend/client/src/context/AuthContext.tsx`, **Lines ~117, ~145**
- **Problem:** `console.error` left in production code. Should use the centralized `logger` utility.
- **Severity:** **Low**
- **Fix:** Replace with `logger.error(…)` from `@/lib/logger`.

---

## Category 5: Unaudited Frontend Components

### 5.1 — `console.error` / `console.log` calls across many components
- **Files and approximate lines:**
  - `MarketPrices.tsx` L84
  - `PnLDashboard.tsx` L86
  - `CostCalculator.tsx` L131, L156, L177, L189, L195
  - `SchemeMatcher.tsx` L81
  - `InsuranceClaims.tsx` L90, L112, L121, L128, L135
  - `PriceForecast.tsx` L69
  - `IrrigationScheduler.tsx` L86, L93, L109
  - `SeasonCalendar.tsx` L84, L100, L109, L116
  - `LaborManager.tsx` L66, L95, L103, L110
  - `InventoryTracker.tsx` L84, L107, L129, L142
  - `EquipmentScheduler.tsx` L92, L111, L126, L133, L140
  - `RotationPlanner.tsx` L63
  - `DataAnalytics.tsx` L57, L67
  - `IndicesReport.tsx` L38
  - `ErrorBoundary.tsx` L29
  - `ExportButton.tsx` L81
  - `ChatBot.tsx` L119
  - `gemini.ts` L55, L62, L100, L159
- **Problem:** Raw `console.error`/`console.warn` calls leak implementation details in production browser consoles.
- **Severity:** **Medium**
- **Fix:** Replace all with `logger.error(…)` / `logger.warn(…)` from `@/lib/logger`. (The logger already exists and is properly environment-aware.)

### 5.2 — `FieldAlerts.tsx` N+1 PATCH calls for "Mark All Read"
- **File:** `frontend/client/src/components/field/FieldAlerts.tsx`, **Lines ~76–79**
- **Problem:** `markAllAsRead` sends individual PATCH requests in a loop. For 50 alerts this fires 50 HTTP requests.
- **Severity:** **Medium**
- **Fix:** Add a backend bulk endpoint (`POST /field/alerts/mark-all-read`) and call it once.

### 5.3 — `Pest.tsx` dead `agroAlerts` state
- **File:** `frontend/client/src/components/field/Pest.tsx`, **Lines ~147–165**
- **Problem:** `agroAlerts` state is initialized as `[]` and never populated. The "Agro Alerts" card renders but always says "No agro-climatic alerts."
- **Severity:** **Medium**
- **Fix:** Either implement the data fetch or remove the dead UI section.

### 5.4 — `MarketPrices.tsx` search input is non-functional
- **File:** `frontend/client/src/components/finance/MarketPrices.tsx`, **Lines ~126–131**
- **Problem:** The search `<input>` has no `onChange` handler and no state binding — it's purely decorative.
- **Severity:** **Medium**
- **Fix:** Bind to a state variable and filter the displayed data, or remove it.

### 5.5 — `DataAnalytics.tsx` hardcoded rice price `₹2,700`
- **File:** `frontend/client/src/components/analytics/DataAnalytics.tsx`, **Lines ~215–225**
- **Problem:** The "Market Price" card shows a hardcoded `₹2,700` and `+2.5%` — this is not fetched from any API.
- **Severity:** **Medium**
- **Fix:** Fetch from the market-prices API or remove the misleading card.

### 5.6 — `DataAnalytics.tsx` tree count always shows `0`
- **File:** `frontend/client/src/components/analytics/DataAnalytics.tsx`, **Lines ~170–180**
- **Problem:** Tree count is hardcoded to `0` with "Last scan: Never". No fetch logic exists.
- **Severity:** **Low**
- **Fix:** Either implement the feature or clearly label it as "Coming Soon."

### 5.7 — `IndicesReport.tsx` NDWI chart uses hardcoded static data
- **File:** `frontend/client/src/components/analytics/IndicesReport.tsx`, **Lines ~85–100**
- **Problem:** The bar chart values `[60, 45, 35, 40, 25, 30, 20]` are hardcoded, not sourced from `data`. The "Current: 0.75" is also hardcoded.
- **Severity:** **Medium**
- **Fix:** Derive chart values from the API response's NDWI time-series data.

### 5.8 — `ErrorBoundary.tsx` leaks error messages to users
- **File:** `frontend/client/src/components/common/ErrorBoundary.tsx`, **Line ~49**
- **Problem:** `this.state.error?.message` is rendered directly to the user. Internal error messages (e.g., stack traces, DB errors) could be exposed.
- **Severity:** **Medium**
- **Fix:** Show a generic error message to users; log the real error via `logger.error()`.

### 5.9 — `PnLDashboard.tsx` Export/Add Entry buttons are non-functional
- **File:** `frontend/client/src/components/finance/PnLDashboard.tsx`, **Lines ~147–154**
- **Problem:** "Export" and "Add Entry" buttons have no `onClick` handlers — they do nothing.
- **Severity:** **Low**
- **Fix:** Wire up to the `ExportButton` component and navigation respectively, or remove.

### 5.10 — `gemini.ts` uses `any` type for payload
- **File:** `frontend/client/src/lib/gemini.ts`, **Line ~143**
- **Problem:** `const payload: any = { … }` — defeats TypeScript safety.
- **Severity:** **Low**
- **Fix:** Define a `ChatPayload` interface and use it.

### 5.11 — `gemini.ts` `console.error` in `askCropQuestion`
- **File:** `frontend/client/src/lib/gemini.ts`, **Line ~159**
- **Problem:** Uses `catch (error: any)` and `console.error` — both the `any` and the raw console call are problematic.
- **Severity:** **Low**
- **Fix:** Type the error properly and use `logger.error(…)`.

---

## Category 6: ML Engine

### 6.1 — All ML files are well-structured
- **Files:** `ml_engine/cnn.py`, `lstm.py`, `health_score.py`, `awd.py`, `cc.py`
- **Problem:** None significant. Good lazy loading, proper fallback predictions, and error handling throughout.
- **Severity:** N/A
- **Note:** Minor improvement — `cnn.py` and `lstm.py` have inline imports inside functions (e.g., `import torch`). This is intentional for lazy loading and is acceptable.

---

## Category 7: Backend `tasks.py`

### 7.1 — All Celery tasks iterate all fields globally without rate limiting
- **File:** `backend/field/tasks.py`, **Lines 35–125**
- **Problem:** `update_weather_data`, `update_satellite_data`, and `calculate_risk_scores` each iterate over **every field for every user** and make individual external API calls (OpenWeatherMap, Earth Engine). With 1000 fields this is 1000+ API calls per task run, risking rate-limit bans and extreme run times.
- **Severity:** **High**
- **Fix:** Batch/deduplicate by location (many fields share coordinates), add rate-limiting with `time.sleep()` or a token-bucket, and consider chunking into sub-tasks via `celery.group`.

### 7.2 — `cleanup_old_logs` deletes all users' logs indiscriminately
- **File:** `backend/field/tasks.py`, **~Line 204**
- **Problem:** Deletes all `FieldLog` records older than 2 years with no per-user opt-out. This is a data-retention policy decision that should be configurable.
- **Severity:** **Medium**
- **Fix:** Make the retention period a setting; consider soft-delete or archiving instead.

---

## Category 8: Frontend `api.ts`

### 8.1 — `console.warn` in retry loop
- **File:** `frontend/client/src/lib/api.ts`, **Line ~173**
- **Problem:** `console.warn(…)` in the retry logic leaks diagnostic info in production.
- **Severity:** **Low**
- **Fix:** Use `logger.warn(…)`.

### 8.2 — Otherwise well-architected
- Centralized `ENDPOINTS` constant, typed `ApiError` class, automatic retry with exponential backoff, proper auth header injection. No other issues found.

---

## Category 9: Backend Middleware

### 9.1 — No issues found
- **File:** `backend/middleware/request_logging.py`
- Well-implemented. Does not log request bodies (good for security). Logs IP addresses and response times. Properly excludes health-check endpoints.

---

## Category 10: Docker / Infrastructure

### 10.1 — `docker-compose.yml` default `POSTGRES_PASSWORD=changeme`
- **File:** `docker-compose.yml`, **~Line 48**
- **Problem:** Insecure default password that will invariably end up in production if someone forgets to override.
- **Severity:** **Critical**
- **Fix:** Remove the default and require it via `.env` file: `POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}`.

### 10.2 — `docker-compose.yml` exposes PostgreSQL port 5432 to host
- **File:** `docker-compose.yml`, **~Line 50**
- **Problem:** `ports: - "5432:5432"` makes the database accessible from the host network (and potentially the internet if the host has a public IP).
- **Severity:** **High**
- **Fix:** For dev, use `ports: - "127.0.0.1:5432:5432"`. For prod, remove entirely and use Docker networking only.

### 10.3 — `docker-compose.prod.yml` mounts source code as volume
- **File:** `docker-compose.prod.yml`, **~Line 69**
- **Problem:** `./backend:/app` volume mount means the production container runs the host's source files instead of the baked-in image code. This defeats the purpose of a Docker image and creates drift.
- **Severity:** **Critical**
- **Fix:** Remove the source-mount volume in the production compose. The code should only come from the built image.

### 10.4 — `docker-compose.prod.yml` Grafana default password `admin`
- **File:** `docker-compose.prod.yml`, **~Line 196**
- **Problem:** `GRAFANA_PASSWORD:-admin` — insecure default for a monitoring dashboard.
- **Severity:** **High**
- **Fix:** Require via `.env` like PostgreSQL.

### 10.5 — `backend/Dockerfile` has no `CMD` instruction
- **File:** `backend/Dockerfile`, **Line 52 (end of file)**
- **Problem:** Dockerfile ends without a `CMD` or `ENTRYPOINT`. The container can only be started by passing the command externally (via compose), reducing portability.
- **Severity:** **Low**
- **Fix:** Add `CMD ["gunicorn", "KrishiSaarthi.wsgi:application", "--bind", "0.0.0.0:8000"]` (or whatever the intended default command is).

---

## Category 11: Security (Cross-Cutting)

### 11.1 — Password reset leaks user existence
- **File:** `backend/KrishiSaarthi/views.py`, **Line 88**
- **Problem:** `return Response({'error': 'User not found'}, status=404)` tells an attacker whether an email/username is registered.
- **Severity:** **Critical**
- **Fix:** Always return the same success message regardless of whether the user exists: `"If an account exists with this email, we have sent a reset link."`

### 11.2 — `ResetPassword` has no password strength validation
- **File:** `backend/KrishiSaarthi/views.py`, **Lines 97–106**
- **Problem:** `user.set_password(password)` accepts any string — empty string, single character, etc. The serializer's `min_length=8` does not apply here.
- **Severity:** **Critical**
- **Fix:** Call `django.contrib.auth.password_validation.validate_password(password, user)` and return errors if it fails.

### 11.3 — Signup double-save
- **File:** `backend/KrishiSaarthi/views.py`, **Lines 42–47**
- **Problem:** `serializer.save()` already creates the user. Then `User.objects.get(username=…)` fetches the same user, calls `set_password()`, and saves again. This is a wasted DB round-trip and means the password is hashed twice.
- **Severity:** **Medium**
- **Fix:** Override `create()` on the serializer to call `set_password()` inside it, eliminating the second `get()` + `save()`.

---

## Summary by Severity

| Severity | Count |
|----------|-------|
| **Critical** | 7 |
| **High** | 9 |
| **Medium** | 14 |
| **Low** | 12 |
| **Total** | **42** |

### Critical Items (fix immediately)
1. `rotation.py` L166–169 — always-False season condition
2. `AuthContext.tsx` — no server-side token validation on mount
3. `docker-compose.yml` — default `POSTGRES_PASSWORD=changeme`
4. `docker-compose.prod.yml` — source code mounted in production
5. `KrishiSaarthi/views.py` L88 — password reset leaks user existence
6. `KrishiSaarthi/views.py` L97–106 — no password validation on reset
7. `docker-compose.yml` — PostgreSQL port exposed to host (when on a public-facing machine)
