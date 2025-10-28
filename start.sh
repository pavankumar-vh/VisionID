#!/bin/bash
# VisionID - Startup Script (Linux/Mac)
# Quick start script for running VisionID API

echo "🚀 Starting VisionID - AI Face Recognition System"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "📚 Checking dependencies..."
if ! pip show fastapi > /dev/null 2>&1; then
    echo "⚙️ Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

echo ""
echo "🌐 Starting FastAPI server..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/ping"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
