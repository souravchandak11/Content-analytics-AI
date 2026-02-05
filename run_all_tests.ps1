# Content Analytics Tool - Test Suite (Windows PowerShell)
# =========================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Content Analytics Tool - Test Suite" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Track test results
$PASSED = 0
$FAILED = 0

# Function to run test and track result
function Run-Test {
    param (
        [string]$TestName,
        [string]$Command
    )
    
    Write-Host "Running: $TestName" -ForegroundColor Yellow
    
    try {
        $result = Invoke-Expression $Command 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ PASSED" -ForegroundColor Green
            $script:PASSED++
        } else {
            Write-Host "✗ FAILED" -ForegroundColor Red
            Write-Host $result -ForegroundColor Gray
            $script:FAILED++
        }
    } catch {
        Write-Host "✗ FAILED (Exception)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Gray
        $script:FAILED++
    }
    Write-Host ""
}

# 1. Environment Check
Write-Host "1️⃣  Environment Configuration Check" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "API Keys Configuration" "python tests/test_env.py"

# 2. API Connection Tests
Write-Host "2️⃣  API Connection Tests" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "YouTube API" "pytest tests/test_api_connections.py::TestAPIConnections::test_youtube_connection -v"
Run-Test "Instagram API" "pytest tests/test_api_connections.py::TestAPIConnections::test_instagram_connection -v"

# 3. Database Tests
Write-Host "3️⃣  Database Tests" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "Database Connection" "pytest tests/test_database.py::TestDatabase::test_database_connection -v"
Run-Test "Data Persistence" "pytest tests/test_database.py::TestDatabase::test_youtube_channel_save -v"

# 4. Analytics Tests
Write-Host "4️⃣  Analytics Tests" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "Engagement Calculations" "pytest tests/test_analytics.py -v"

# 5. Data Quality Check
Write-Host "5️⃣  Data Quality Validation" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "Data Quality" "python tests/validate_data_quality.py"

# 6. Performance Tests
Write-Host "6️⃣  Performance Tests" -ForegroundColor Magenta
Write-Host "-----------------------------------"
Run-Test "Query Performance" "python tests/test_performance.py"

# 7. ML Model Tests (if models exist)
if (Test-Path "data/models") {
    Write-Host "7️⃣  ML Model Tests" -ForegroundColor Magenta
    Write-Host "-----------------------------------"
    Run-Test "Model Validation" "pytest tests/test_ml_models.py -v"
}

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Passed: $PASSED" -ForegroundColor Green
Write-Host "Failed: $FAILED" -ForegroundColor Red
Write-Host ""

if ($FAILED -eq 0) {
    Write-Host "✅ ALL TESTS PASSED - PROJECT READY!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  SOME TESTS FAILED - REVIEW ERRORS ABOVE" -ForegroundColor Red
    exit 1
}
