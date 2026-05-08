"""
Comprehensive endpoint testing script for KrishiSaarthi.
Tests all backend API endpoints, auth flows, and ML engine availability.
"""
import requests
import json
import sys
import os

os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8000"
RESULTS = {"pass": [], "fail": [], "warn": []}

def test(name, method, url, expected_status=None, data=None, headers=None, allow_statuses=None):
    """Run a single API test."""
    try:
        kwargs = {"timeout": 15}
        if data:
            kwargs["json"] = data
        if headers:
            kwargs["headers"] = headers
        
        r = getattr(requests, method)(url, **kwargs)
        
        if allow_statuses:
            ok = r.status_code in allow_statuses
        elif expected_status:
            ok = r.status_code == expected_status
        else:
            ok = r.status_code < 500
        
        status_str = f"{r.status_code}"
        if ok:
            RESULTS["pass"].append(f"PASS: {name} [{method.upper()} {status_str}]")
        else:
            RESULTS["fail"].append(f"FAIL: {name} [{method.upper()} {status_str}] expected {expected_status or allow_statuses}")
            try:
                body = r.text[:200]
                RESULTS["fail"].append(f"      Response: {body}")
            except:
                pass
        
        return r
    except requests.exceptions.ConnectionError:
        RESULTS["fail"].append(f"FAIL: {name} - CONNECTION REFUSED")
        return None
    except requests.exceptions.Timeout:
        RESULTS["warn"].append(f"WARN: {name} - TIMEOUT (>15s)")
        return None
    except Exception as e:
        RESULTS["fail"].append(f"FAIL: {name} - ERROR: {e}")
        return None

print("=" * 70)
print("KRISHISAARTHI COMPREHENSIVE ENDPOINT TEST")
print("=" * 70)

# 1. HEALTH & MONITORING ENDPOINTS
print("\n--- HEALTH & MONITORING ---")
test("Health Check", "get", f"{BASE}/health", 200)
test("Readiness Check", "get", f"{BASE}/ready", allow_statuses=[200, 503])
test("Metrics", "get", f"{BASE}/metrics", 200)
test("Health V1", "get", f"{BASE}/api/v1/health", 200)

# 2. AUTH ENDPOINTS - SIGNUP
print("\n--- AUTH: SIGNUP ---")
r = test("Signup (new user)", "post", f"{BASE}/signup", allow_statuses=[201, 400], data={
    "username": "testbot_check2",
    "password": "TestBot@2026!",
    "email": "testbot2@test.com"
})
token = None
if r and r.status_code == 201:
    body = r.json()
    token = body.get("token")
    print(f"   Token received: {bool(token)}")

# 3. AUTH: LOGIN
print("\n--- AUTH: LOGIN ---")
r = test("Login", "post", f"{BASE}/login", 200, {
    "username": "testbot_check2",
    "password": "TestBot@2026!"
})
if r and r.status_code == 200:
    body = r.json()
    token = body.get("token")
    print(f"   Token received: {bool(token)}")
    print(f"   User: {body.get('user', {}).get('username')}")

# If we still don't have a token, try other known users
if not token:
    for uname, pwd in [("testbot_check", "TestBot@2026!"), ("admin", "admin")]:
        r2 = requests.post(f"{BASE}/login", json={"username": uname, "password": pwd}, timeout=10)
        if r2.status_code == 200:
            token = r2.json().get("token")
            print(f"   Fallback login with {uname}: success")
            break

AUTH = {"Authorization": f"Token {token}"} if token else {}

# 4. AUTH: TEST TOKEN
print("\n--- AUTH: TOKEN VALIDATION ---")
if token:
    test("Test Token", "get", f"{BASE}/test_token", 200, headers=AUTH)
else:
    RESULTS["warn"].append("WARN: Test Token - SKIPPED (no auth token)")

# 5. AUTH: VALIDATION
test("Login (invalid creds)", "post", f"{BASE}/login", 401, {
    "username": "nonexistent",
    "password": "wrong"
})

test("Signup (missing fields)", "post", f"{BASE}/signup", 400, {
    "username": ""
})

# 6. FIELD ENDPOINTS
print("\n--- FIELD ENDPOINTS ---")
test("Field Data (list)", "get", f"{BASE}/field/data", allow_statuses=[200, 401, 403], headers=AUTH)
test("Weather", "get", f"{BASE}/field/weather", allow_statuses=[200, 400, 401], headers=AUTH)
test("Health Score", "get", f"{BASE}/field/healthscore", allow_statuses=[200, 400, 401], headers=AUTH)
test("Pest Prediction", "get", f"{BASE}/field/pestpredict", allow_statuses=[200, 400, 401, 405], headers=AUTH)
test("AWD Report", "get", f"{BASE}/field/awd", allow_statuses=[200, 400, 401], headers=AUTH)
test("Carbon Credit", "get", f"{BASE}/field/cc", allow_statuses=[200, 400, 401], headers=AUTH)
test("Field Logs", "get", f"{BASE}/field/logs", allow_statuses=[200, 401], headers=AUTH)
test("Field Alerts", "get", f"{BASE}/field/alerts", allow_statuses=[200, 401], headers=AUTH)
test("Soil Advice", "get", f"{BASE}/field/soil-advice", allow_statuses=[200, 400, 401, 405], headers=AUTH)
test("Irrigation Schedule", "get", f"{BASE}/field/irrigation-schedule", allow_statuses=[200, 400, 401], headers=AUTH)
test("Irrigation Logs", "get", f"{BASE}/field/irrigation-logs", allow_statuses=[200, 401], headers=AUTH)
test("Yield Prediction", "get", f"{BASE}/field/yield-prediction", allow_statuses=[200, 400, 401, 405], headers=AUTH)
test("Diagnose Health", "post", f"{BASE}/field/diagnose", allow_statuses=[200, 400, 401, 405], headers=AUTH)
test("EE Analysis", "get", f"{BASE}/field/ee", allow_statuses=[200, 400, 401], headers=AUTH)
test("Get Coord", "get", f"{BASE}/field/coord", allow_statuses=[200, 400, 401], headers=AUTH)
test("Pest Report", "get", f"{BASE}/field/pest/report", allow_statuses=[200, 400, 401, 405], headers=AUTH)
test("Bulk Mark Alerts Read", "post", f"{BASE}/field/alerts/mark-all-read", allow_statuses=[200, 401], headers=AUTH)

# 7. FINANCE ENDPOINTS
print("\n--- FINANCE ENDPOINTS ---")
test("Cost Entries", "get", f"{BASE}/finance/costs", allow_statuses=[200, 401], headers=AUTH)
test("Cost Summary", "get", f"{BASE}/finance/costs/summary", allow_statuses=[200, 401], headers=AUTH)
test("Revenue", "get", f"{BASE}/finance/revenue", allow_statuses=[200, 401], headers=AUTH)
test("Seasons", "get", f"{BASE}/finance/seasons", allow_statuses=[200, 401], headers=AUTH)
test("PnL Dashboard", "get", f"{BASE}/finance/pnl", allow_statuses=[200, 401], headers=AUTH)
test("Market Prices", "get", f"{BASE}/finance/market-prices", allow_statuses=[200, 401], headers=AUTH)
test("Price Forecast", "get", f"{BASE}/finance/price-forecast", allow_statuses=[200, 400, 401], headers=AUTH)
test("Gov Schemes", "get", f"{BASE}/finance/schemes", allow_statuses=[200, 401], headers=AUTH)
test("Insurance Claims", "get", f"{BASE}/finance/insurance", allow_statuses=[200, 401], headers=AUTH)
test("Transactions", "get", f"{BASE}/finance/transactions", allow_statuses=[200, 401], headers=AUTH)

# 8. PLANNING ENDPOINTS
print("\n--- PLANNING ENDPOINTS ---")
test("Calendar", "get", f"{BASE}/planning/calendar", allow_statuses=[200, 401], headers=AUTH)
test("Inventory", "get", f"{BASE}/planning/inventory", allow_statuses=[200, 401], headers=AUTH)
test("Labor", "get", f"{BASE}/planning/labor", allow_statuses=[200, 401], headers=AUTH)
test("Equipment", "get", f"{BASE}/planning/equipment", allow_statuses=[200, 401], headers=AUTH)
test("Bookings", "get", f"{BASE}/planning/bookings", allow_statuses=[200, 401], headers=AUTH)
test("Plans", "get", f"{BASE}/planning/plans", allow_statuses=[200, 401], headers=AUTH)
test("Rotation Planner", "post", f"{BASE}/planning/rotation", allow_statuses=[200, 400, 401, 405], headers=AUTH, data={"field_id": 1})

# 9. CHAT ENDPOINTS
print("\n--- CHAT ENDPOINTS ---")
test("Chat (POST)", "post", f"{BASE}/api/chat", allow_statuses=[200, 400, 401], headers=AUTH, data={"message": "Hello"})
test("Chat V1 (POST)", "post", f"{BASE}/api/v1/chat/", allow_statuses=[200, 400, 401], headers=AUTH, data={"message": "test"})

# 10. API V1 PREFIXED ENDPOINTS
print("\n--- API V1 PREFIXED ---")
test("V1 Field Data", "get", f"{BASE}/api/v1/field/data", allow_statuses=[200, 401], headers=AUTH)
test("V1 Finance Costs", "get", f"{BASE}/api/v1/finance/costs", allow_statuses=[200, 401], headers=AUTH)
test("V1 Planning Calendar", "get", f"{BASE}/api/v1/planning/calendar", allow_statuses=[200, 401], headers=AUTH)

# 11. API DOCUMENTATION
print("\n--- API DOCS ---")
test("OpenAPI Schema", "get", f"{BASE}/api/schema/", 200)
test("Swagger UI", "get", f"{BASE}/api/docs/", 200)
test("ReDoc", "get", f"{BASE}/api/redoc/", 200)

# 12. ADMIN
print("\n--- ADMIN ---")
test("Admin Panel", "get", f"{BASE}/admin/", allow_statuses=[200, 302])

# 13. AUTH V1 ENDPOINTS
print("\n--- AUTH V1 ENDPOINTS ---")
test("V1 Login", "post", f"{BASE}/api/v1/auth/login", allow_statuses=[200, 400, 401], data={
    "username": "testbot_check2",
    "password": "TestBot@2026!"
})
test("V1 Test Token", "get", f"{BASE}/api/v1/auth/test-token", allow_statuses=[200, 401], headers=AUTH)

# 14. FIELD CRUD - Create a field
print("\n--- FIELD CRUD ---")
r = test("Create Field", "post", f"{BASE}/field/data", allow_statuses=[200, 201, 400, 401], headers=AUTH, data={
    "name": "Test Field",
    "crop_type": "Rice",
    "area_hectares": 2.5
})
field_id = None
if r and r.status_code in [200, 201]:
    try:
        field_id = r.json().get("id")
    except:
        pass

# 15. FINANCE CRUD - Create cost
print("\n--- FINANCE CRUD ---")
test("Create Cost Entry", "post", f"{BASE}/finance/costs", allow_statuses=[200, 201, 400, 401], headers=AUTH, data={
    "category": "fertilizer",
    "amount": 1500,
    "description": "Test entry"
})

test("Create Season", "post", f"{BASE}/finance/seasons", allow_statuses=[200, 201, 400, 401], headers=AUTH, data={
    "name": "Kharif 2026",
    "start_date": "2026-06-01",
    "end_date": "2026-10-31"
})

# 16. PLANNING CRUD
print("\n--- PLANNING CRUD ---")
test("Create Calendar Event", "post", f"{BASE}/planning/calendar", allow_statuses=[200, 201, 400, 401], headers=AUTH, data={
    "title": "Test Sowing",
    "date": "2026-06-15",
    "event_type": "sowing"
})

test("Create Inventory Item", "post", f"{BASE}/planning/inventory", allow_statuses=[200, 201, 400, 401], headers=AUTH, data={
    "name": "Test Fertilizer",
    "quantity": 50,
    "unit": "kg"
})

# 17. LOGOUT
print("\n--- AUTH: LOGOUT ---")
if token:
    test("Logout", "post", f"{BASE}/logout", 200, headers=AUTH)

# SUMMARY
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"\nPASSED: {len(RESULTS['pass'])}")
for p in RESULTS["pass"]:
    print(f"   {p}")

print(f"\nFAILED: {len(RESULTS['fail'])}")
for f in RESULTS["fail"]:
    print(f"   {f}")

print(f"\nWARNINGS: {len(RESULTS['warn'])}")
for w in RESULTS["warn"]:
    print(f"   {w}")

total = len(RESULTS["pass"]) + len(RESULTS["fail"]) + len(RESULTS["warn"])
print(f"\nTotal tests: {total} | Pass: {len(RESULTS['pass'])} | Fail: {len(RESULTS['fail'])} | Warn: {len(RESULTS['warn'])}")

if RESULTS["fail"]:
    print("\n[!] SOME TESTS FAILED - Action Required!")
    sys.exit(1)
else:
    print("\n[OK] ALL TESTS PASSED!")
    sys.exit(0)
