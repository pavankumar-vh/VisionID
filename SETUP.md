# VisionID - Complete Setup Guide

## 🎯 Phase 1 - Project Setup & Structure (COMPLETED ✅)

This guide will help you get VisionID up and running on your system.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Docker** (Optional, for containerized deployment) ([Download](https://www.docker.com/))
- **NVIDIA GPU + CUDA** (Optional, for GPU acceleration)

---

## 🚀 Quick Start

### Windows (PowerShell)

```powershell
# Navigate to project directory
cd "f:\OPENSOURCE\aiproject detection\VisionID"

# Run startup script
.\start.ps1
```

### Linux/Mac

```bash
# Navigate to project directory
cd /path/to/VisionID

# Make script executable
chmod +x start.sh

# Run startup script
./start.sh
```

---

## 📦 Manual Installation

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Note**: If you encounter issues with `insightface`, install these first:
```bash
pip install numpy opencv-python
pip install onnxruntime  # or onnxruntime-gpu for GPU
pip install insightface
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# (Optional: update DATABASE_URL, GPU settings, etc.)
```

### Step 4: Run the Application

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🐳 Docker Installation

### Option 1: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Docker Only

```bash
# Build image
docker build -t visionid:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --name visionid \
  visionid:latest

# View logs
docker logs -f visionid

# Stop container
docker stop visionid
```

---

## 🧪 Verify Installation

### 1. Check API Health

```bash
curl http://localhost:8000/ping
```

Expected response:
```json
{
  "status": "VisionID API active",
  "version": "1.0.0",
  "message": "AI Face Recognition System is operational"
}
```

### 2. Access API Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Run Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Run all tests
pytest test_visionid.py -v

# Run with coverage
pytest test_visionid.py --cov=app
```

---

## 🎯 What's Next?

### Phase 2: Face Detection Implementation
- Implement InsightFace RetinaFace detector
- Add face preprocessing
- Test detection endpoints

### Phase 3: Face Recognition & Matching
- Implement ArcFace embedding generation
- Add face matching algorithm
- Test recognition endpoints

### Phase 4: Database Integration
- Initialize database tables
- Implement user registration
- Store face embeddings

### Phase 5: Attendance System
- Implement attendance marking
- Add reporting features
- Test attendance workflows

---

## 🔧 Troubleshooting

### Issue: ImportError for InsightFace

**Solution**:
```bash
pip install --upgrade insightface
pip install onnxruntime  # or onnxruntime-gpu
```

### Issue: OpenCV Import Error

**Solution**:
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

### Issue: Database Connection Error

**Solution**:
1. Check DATABASE_URL in `.env`
2. For SQLite (default), no setup needed
3. For PostgreSQL, ensure database exists:
```bash
createdb visionid_db
```

### Issue: Port 8000 Already in Use

**Solution**:
```bash
# Use different port
uvicorn app.main:app --port 8001

# Or kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or kill process on port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9
```

---

## 📊 Project Structure Overview

```
visionid/
├── app/
│   ├── main.py              # FastAPI app with CORS, routes
│   ├── routes/              # API endpoints
│   │   ├── recognize.py     # Face recognition endpoints
│   │   ├── register.py      # User registration endpoints
│   │   └── attendance.py    # Attendance tracking endpoints
│   ├── services/            # Business logic
│   │   ├── detector.py      # Face detection service
│   │   ├── embedder.py      # Face embedding service
│   │   └── matcher.py       # Face matching service
│   ├── models/              # Database models
│   │   ├── database.py      # DB configuration
│   │   ├── user.py          # User & attendance models
│   │   └── crud.py          # Database operations
│   └── utils/               # Helper functions
│       ├── image_utils.py   # Image processing
│       └── logger.py        # Logging utilities
├── data/
│   └── embeddings/          # Stored face embeddings
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-container setup
├── .env.example            # Environment template
├── start.ps1               # Windows startup script
├── start.sh                # Linux/Mac startup script
└── test_visionid.py        # Test suite
```

---

## 🔐 Security Notes

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use strong database passwords** - Especially in production
3. **Enable HTTPS** - Use reverse proxy (nginx) with SSL
4. **Add API authentication** - Implement API keys or OAuth
5. **Limit CORS origins** - Replace `*` with specific domains in production

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [InsightFace Documentation](https://github.com/deepinsight/insightface)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)

---

## ✅ Phase 1 Checklist

- [x] Project structure created
- [x] FastAPI app with CORS middleware
- [x] Health check endpoint (`/ping`)
- [x] Three route modules (recognize, register, attendance)
- [x] Service modules (detector, embedder, matcher)
- [x] Database models (User, AttendanceLog, RecognitionHistory)
- [x] Utility modules (image_utils, logger)
- [x] requirements.txt with all dependencies
- [x] Dockerfile and docker-compose.yml
- [x] Test suite
- [x] Comprehensive README
- [x] Setup scripts for Windows and Linux

---

## 🎉 Success!

Your VisionID project is now set up and ready for Phase 2 development!

Access your API at: **http://localhost:8000/docs**

Happy coding! 🚀
