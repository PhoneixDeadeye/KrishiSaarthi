# Troubleshooting Guide

## 503 Service Unavailable Errors

### Problem
API endpoints returning 503 errors:
- `/field/ee?field_id=1`
- `/field/healthscore`
- `/field/awd?field_id=1`
- `/field/pestpredict?field_id=1`

### Root Cause
Google Earth Engine is not properly authenticated, causing the circuit breaker to block satellite data requests.

### Solution

#### Option 1: Authenticate with Google Cloud CLI (Recommended for Development)

1. **Install Google Cloud SDK**:
   ```powershell
   # Download and install from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Earth Engine**:
   ```powershell
   # Login to Google Cloud
   gcloud auth login
   
   # Set your project
   gcloud config set project crop-capstone
   
   # Authenticate Earth Engine
   earthengine authenticate
   ```

3. **Verify authentication**:
   ```powershell
   earthengine authenticate --status
   ```

4. **Restart the backend server** to pick up the new credentials.

#### Option 2: Use Service Account (Recommended for Production)

1. **Create a Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to IAM & Admin > Service Accounts
   - Create new service account with Earth Engine API access
   - Download the JSON key file

2. **Add credentials to your project**:
   ```powershell
   # Create credentials directory
   mkdir backend/credentials
   
   # Copy your service account JSON file
   # Rename it to: gee-service-account.json
   ```

3. **Update backend/.env**:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=credentials/gee-service-account.json
   GEE_PROJECT=crop-capstone
   ```

4. **Update .gitignore** to exclude credentials:
   ```gitignore
   backend/credentials/
   *.json
   ```

5. **Restart the backend server**.

#### Option 3: Disable Earth Engine Features (Development Fallback)

If you don't need satellite data temporarily:

1. **Modify backend/field/services/ee_service.py**:
   ```python
   # Add at the top of fetchEEData_safe function:
   return {
       "error": "Earth Engine disabled",
       "fallback": True,
       "mock_data": True
   }
   ```

2. This will return mock data instead of real satellite imagery.

---

## Browser Extension Errors

### Problem
```
contentScript.js:1 Uncaught (in promise) TypeError: Cannot destructure property 'rate' of '(intermediate value)' as it is undefined.
```

### Root Cause
This error is from a **browser extension** (likely a grammar checker, ad blocker, or similar), NOT from your application code.

### Solution

1. **Disable browser extensions** temporarily:
   - Open Chrome/Edge DevTools (F12)
   - Try the app in an **Incognito/Private window**
   - Or disable extensions one by one to find the culprit

2. **Common culprits**:
   - Grammarly
   - Honey
   - AdBlock/uBlock
   - Password managers

3. This error **does not affect** your application functionality.

---

## Missing Assets (favicon.ico, logo.png)

### Problem
```
GET http://localhost:5173/favicon.ico 404 (Not Found)
GET http://localhost:5173/logo.png 404 (Not Found)
```

### Solution

Assets have been created. To ensure they're served correctly:

1. **Convert logo.svg to PNG**:
   ```powershell
   # Option A: Use online converter
   # Go to: https://cloudconvert.com/svg-to-png
   # Upload: frontend/client/public/logo.svg
   # Download and save as: frontend/client/public/logo.png
   
   # Option B: Use ImageMagick (if installed)
   magick convert frontend/client/public/logo.svg -resize 512x512 frontend/client/public/logo.png
   ```

2. **Create favicon.ico**:
   ```powershell
   # Go to: https://www.favicon-generator.org/
   # Upload the logo.png
   # Download favicon.ico
   # Place in: frontend/client/public/favicon.ico
   ```

3. **Update index.html** (if needed):
   Make sure `frontend/client/index.html` has:
   ```html
   <link rel="icon" type="image/x-icon" href="/favicon.ico">
   ```

4. **Restart the development server**:
   ```powershell
   # From frontend directory
   npm run dev
   ```

---

## Verifying the Fix

After applying the Earth Engine authentication fix:

1. **Check backend health**:
   ```powershell
   curl http://localhost:8000/api/readiness/
   ```
   
   Should return:
   ```json
   {
     "status": "ready",
     "checks": {
       "database": true,
       "ml_models": true,
       "earth_engine": true
     }
   }
   ```

2. **Test API endpoints**:
   ```powershell
   # Test weather (should work without Earth Engine)
   curl "http://localhost:8000/field/weather?lat=28.6139&lon=77.2090"
   
   # Test Earth Engine (should work after authentication)
   curl -H "Authorization: Token YOUR_TOKEN" "http://localhost:8000/field/ee?field_id=1"
   ```

3. **Check browser console** - should see no more 503 errors on the Dashboard page.

---

## Additional Help

### Enable Debug Logging

To see more detailed error messages:

1. **Backend logs**: Already enabled with `DEBUG=True` in your .env
2. **Check Django logs**:
   ```powershell
   # Backend logs are in: backend/logs/
   tail -f backend/logs/app.log
   ```

### Contact Support

If issues persist:
- Check the [GitHub Issues](https://github.com/your-repo/issues)
- Review the setup guide: [QUICKSTART.md](QUICKSTART.md)
- Ensure all dependencies are installed: `pip install -r requirements.txt`
