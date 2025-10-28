# VisionID - Startup Script
# Quick start script for running VisionID API

Write-Host "🚀 Starting VisionID - AI Face Recognition System" -ForegroundColor Green
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "📚 Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list

if ($pipList -notmatch "fastapi") {
    Write-Host "⚙️ Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "📖 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏥 Health Check: http://localhost:8000/ping" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
