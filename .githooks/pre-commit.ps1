#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Pre-commit hook for code quality checks
.DESCRIPTION
    Runs linting, formatting, and tests before allowing commit
#>

param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔍 Pre-commit checks..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

$failed = $false

# Check Python files
Write-Host "📝 Checking Python code..." -ForegroundColor Yellow

Push-Location "backend"
try {
    # Get staged Python files
    $pyFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.py$' }
    
    if ($pyFiles) {
        Write-Host "  Found $($pyFiles.Count) Python files to check" -ForegroundColor Gray
        
        # Check for syntax errors
        foreach ($file in $pyFiles) {
            if (Test-Path $file) {
                python -m py_compile $file 2>&1 | Out-Null
                if ($LASTEXITCODE -ne 0) {
                    Write-Host "  ✗ Syntax error in $file" -ForegroundColor Red
                    $failed = $true
                }
            }
        }
        
        if (-not $failed) {
            Write-Host "  ✓ Python syntax check passed" -ForegroundColor Green
        }
    } else {
        Write-Host "  ℹ No Python files to check" -ForegroundColor Gray
    }
}
finally {
    Pop-Location
}

Write-Host ""

# Check JavaScript/TypeScript files
Write-Host "⚛️  Checking frontend code..." -ForegroundColor Yellow

Push-Location "frontend"
try {
    $jsFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.(js|jsx|ts|tsx)$' }
    
    if ($jsFiles -and (Test-Path "node_modules")) {
        Write-Host "  Found $($jsFiles.Count) files to check" -ForegroundColor Gray
        
        # Run ESLint if available
        if (Test-Path "node_modules/.bin/eslint.cmd") {
            npm run lint --silent 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✓ Frontend lint check passed" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ Linting issues found (not blocking)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  ℹ No frontend files to check" -ForegroundColor Gray
    }
}
finally {
    Pop-Location
}

Write-Host ""

# Run tests (if not skipped)
if (-not $SkipTests) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    
    Push-Location "backend"
    try {
        python manage.py test --verbosity=0 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Tests passed" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Tests failed" -ForegroundColor Red
            $failed = $true
        }
    }
    finally {
        Pop-Location
    }
    
    Write-Host ""
}

# Check for secrets
Write-Host "🔒 Checking for secrets..." -ForegroundColor Yellow

$secrets = git diff --cached | Select-String -Pattern "(password|secret|api_key|token)\s*=\s*['\"](?!your-|test-|fake-)[^'\"]{8,}" -CaseSensitive:$false

if ($secrets) {
    Write-Host "  ⚠ Potential secrets found in staged files:" -ForegroundColor Yellow
    $secrets | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    Write-Host "  Please verify these are not real credentials!" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ No obvious secrets found" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan

# Result
if ($failed) {
    Write-Host "`n❌ Pre-commit checks failed!" -ForegroundColor Red
    Write-Host "Fix the issues above and try again." -ForegroundColor Yellow
    Write-Host "To skip checks: git commit --no-verify" -ForegroundColor Gray
    exit 1
} else {
    Write-Host "`n✅ Pre-commit checks passed!" -ForegroundColor Green
    exit 0
}
