# Earth Engine Authentication Helper Script
# Run this script to authenticate Google Earth Engine

Write-Host "=== Google Earth Engine Authentication ===" -ForegroundColor Green
Write-Host ""

# Check if earthengine-api is installed
Write-Host "Checking if earthengine-api is installed..." -ForegroundColor Yellow
try {
    $eeCheck = python -c "import ee; print(ee.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ earthengine-api is installed (version: $eeCheck)" -ForegroundColor Green
    } else {
        Write-Host "✗ earthengine-api is NOT installed" -ForegroundColor Red
        Write-Host ""
        Write-Host "Installing earthengine-api..." -ForegroundColor Yellow
        cd backend
        pip install earthengine-api
        cd ..
    }
} catch {
    Write-Host "✗ Error checking earthengine-api" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Authentication Options ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose an authentication method:"
Write-Host "1. Authenticate with Google Cloud CLI (Recommended for Development)"
Write-Host "2. Use Service Account (Recommended for Production)"
Write-Host "3. Skip authentication (Features will be disabled)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "=== Google Cloud CLI Authentication ===" -ForegroundColor Cyan
        Write-Host ""
        
        # Check if gcloud is installed
        Write-Host "Checking if Google Cloud CLI is installed..." -ForegroundColor Yellow
        try {
            $gcloudVersion = gcloud version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Google Cloud CLI is installed" -ForegroundColor Green
            } else {
                throw "Not installed"
            }
        } catch {
            Write-Host "✗ Google Cloud CLI is NOT installed" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please install Google Cloud CLI from:" -ForegroundColor Yellow
            Write-Host "https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "After installation, run this script again." -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host ""
        Write-Host "Step 1: Login to Google Cloud" -ForegroundColor Yellow
        gcloud auth login
        
        Write-Host ""
        Write-Host "Step 2: Set your project" -ForegroundColor Yellow
        $project = Read-Host "Enter your GCP project ID (or press Enter for 'crop-capstone')"
        if ([string]::IsNullOrWhiteSpace($project)) {
            $project = "crop-capstone"
        }
        gcloud config set project $project
        
        Write-Host ""
        Write-Host "Step 3: Authenticate Earth Engine" -ForegroundColor Yellow
        earthengine authenticate
        
        Write-Host ""
        Write-Host "Step 4: Verify authentication" -ForegroundColor Yellow
        python -c "import ee; ee.Initialize(project='$project'); print('✓ Earth Engine authenticated successfully!')"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✓ Authentication successful!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Now restart your backend server:" -ForegroundColor Yellow
            Write-Host "  cd backend" -ForegroundColor Cyan
            Write-Host "  python manage.py runserver" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "✗ Authentication failed. Please check the error messages above." -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "=== Service Account Authentication ===" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Follow these steps:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Go to Google Cloud Console:" -ForegroundColor White
        Write-Host "   https://console.cloud.google.com/" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "2. Navigate to: IAM & Admin > Service Accounts" -ForegroundColor White
        Write-Host ""
        Write-Host "3. Create a new service account with Earth Engine API access" -ForegroundColor White
        Write-Host ""
        Write-Host "4. Download the JSON key file" -ForegroundColor White
        Write-Host ""
        Write-Host "5. Save it to: backend/credentials/gee-service-account.json" -ForegroundColor White
        Write-Host ""
        
        $proceed = Read-Host "Have you created and downloaded the service account key? (y/n)"
        
        if ($proceed -eq "y" -or $proceed -eq "Y") {
            # Create credentials directory if it doesn't exist
            if (-not (Test-Path "backend/credentials")) {
                New-Item -ItemType Directory -Path "backend/credentials" | Out-Null
                Write-Host "✓ Created backend/credentials directory" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "Please copy your service account JSON file to:" -ForegroundColor Yellow
            Write-Host "  backend/credentials/gee-service-account.json" -ForegroundColor Cyan
            Write-Host ""
            
            $keyPath = Read-Host "Enter the path to your JSON key file (or press Enter to skip)"
            
            if (-not [string]::IsNullOrWhiteSpace($keyPath)) {
                if (Test-Path $keyPath) {
                    Copy-Item $keyPath -Destination "backend/credentials/gee-service-account.json"
                    Write-Host "✓ Service account key copied successfully" -ForegroundColor Green
                } else {
                    Write-Host "✗ File not found: $keyPath" -ForegroundColor Red
                }
            }
            
            # Update .env file
            Write-Host ""
            Write-Host "Updating backend/.env..." -ForegroundColor Yellow
            $envPath = "backend/.env"
            $envContent = Get-Content $envPath -Raw
            
            if ($envContent -notmatch "GOOGLE_APPLICATION_CREDENTIALS") {
                Add-Content -Path $envPath -Value "`nGOOGLE_APPLICATION_CREDENTIALS=credentials/gee-service-account.json"
                Write-Host "✓ Added GOOGLE_APPLICATION_CREDENTIALS to .env" -ForegroundColor Green
            } else {
                Write-Host "✓ GOOGLE_APPLICATION_CREDENTIALS already in .env" -ForegroundColor Green
            }
            
            # Update .gitignore
            Write-Host ""
            Write-Host "Updating .gitignore..." -ForegroundColor Yellow
            $gitignorePath = ".gitignore"
            $gitignoreContent = ""
            if (Test-Path $gitignorePath) {
                $gitignoreContent = Get-Content $gitignorePath -Raw
            }
            
            if ($gitignoreContent -notmatch "backend/credentials") {
                Add-Content -Path $gitignorePath -Value "`nbackend/credentials/`n*.json"
                Write-Host "✓ Added credentials to .gitignore" -ForegroundColor Green
            } else {
                Write-Host "✓ Credentials already in .gitignore" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "✓ Service account setup complete!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Now restart your backend server:" -ForegroundColor Yellow
            Write-Host "  cd backend" -ForegroundColor Cyan
            Write-Host "  python manage.py runserver" -ForegroundColor Cyan
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Earth Engine features will be disabled." -ForegroundColor Yellow
        Write-Host "The application will show 'Service temporarily unavailable' messages." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You can authenticate later by running this script again." -ForegroundColor Cyan
    }
    
    default {
        Write-Host ""
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. Restart your backend server" -ForegroundColor White
Write-Host "2. Check the health endpoint: http://localhost:8000/api/readiness/" -ForegroundColor White
Write-Host "3. Verify 'earth_engine: true' in the response" -ForegroundColor White
Write-Host ""
Write-Host "For more help, see: TROUBLESHOOTING.md" -ForegroundColor Cyan
Write-Host ""
