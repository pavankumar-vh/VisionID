# VisionID 🎯

## AI Face Recognition & Attendance System (99% Accuracy)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![InsightFace](https://img.shields.io/badge/InsightFace-0.7-orange.svg)](https://github.com/deepinsight/insightface)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**VisionID** is a real-time, high-accuracy face recognition system built with **FastAPI** and **InsightFace**, powered by GPU acceleration for blazing-fast performance.

---

## 🚀 Features

✅ **99%+ Accuracy** - Powered by InsightFace's ArcFace model  
✅ **Real-time Detection** - RetinaFace for fast face detection  
✅ **Async API** - FastAPI for high-performance async operations  
✅ **Multiple Faces** - Detect and recognize multiple faces simultaneously  
✅ **Attendance System** - Built-in attendance tracking & reporting  
✅ **GPU Accelerated** - CUDA/cuDNN support for maximum speed  
✅ **REST API** - Complete API with Swagger documentation  
✅ **Docker Ready** - Containerized for easy deployment  
✅ **Database Support** - SQLite for demo, PostgreSQL for production  

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | Async web framework |
| **AI Model** | InsightFace (ArcFace + RetinaFace) | Face recognition & detection |
| **Language** | Python 3.10+ | ML ecosystem support |
| **Database** | PostgreSQL / SQLite | User & attendance data |
| **ORM** | SQLAlchemy | Database management |
| **Validation** | Pydantic v2 | Schema validation |
| **Deployment** | Docker + Uvicorn | Containerized runtime |
| **Testing** | Pytest + HTTPX | Unit & integration tests |

---

## 📁 Project Structure

```
visionid/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── routes/
│   │   ├── recognize.py        # Recognition endpoints
│   │   ├── register.py         # Registration endpoints
│   │   └── attendance.py       # Attendance endpoints
│   ├── services/
│   │   ├── detector.py         # Face detection service
│   │   ├── embedder.py         # Face embedding service
│   │   └── matcher.py          # Face matching service
│   ├── models/
│   │   ├── database.py         # Database configuration
│   │   ├── user.py             # User models
│   │   └── crud.py             # Database operations
│   └── utils/
│       ├── image_utils.py      # Image processing utilities
│       └── logger.py           # Logging configuration
├── data/
│   └── embeddings/             # Stored face embeddings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── test_visionid.py           # Test suite
└── README.md                   # This file
```

---

## 🛠️ Installation

### Option 1: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/visionid.git
cd visionid

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload
```

### Option 2: Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build Docker image manually
docker build -t visionid .
docker run -p 8000:8000 visionid
```

**For detailed production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

---

## 🎯 Quick Start

### 1. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Test Health Check

```bash
curl http://localhost:8000/ping
```

Response:
```json
{
  "status": "VisionID API active",
  "version": "1.0.0",
  "message": "AI Face Recognition System is operational"
}
```

---

## 📡 API Endpoints

### Health & Info
- `GET /` - Root endpoint with API info
- `GET /ping` - Health check

### Registration
- `POST /api/v1/register` - Register new user with face
- `GET /api/v1/register/users` - List all registered users
- `PUT /api/v1/register/user/{user_id}` - Update user
- `DELETE /api/v1/register/user/{user_id}` - Delete user

### Recognition
- `POST /api/v1/recognize` - Recognize faces in image
- `POST /api/v1/recognize/video` - Recognize faces in video frame
- `GET /api/v1/recognize/history` - Get recognition history

### Attendance
- `POST /api/v1/attendance/mark` - Mark attendance
- `GET /api/v1/attendance/today` - Get today's attendance
- `GET /api/v1/attendance/report` - Generate attendance report
- `GET /api/v1/attendance/user/{user_id}` - Get user attendance
- `GET /api/v1/attendance/statistics` - Get attendance statistics

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest test_visionid.py -v

# Run with coverage
pytest test_visionid.py --cov=app --cov-report=html
```

---

## ⚙️ Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Key configuration options:

```env
# Database
DATABASE_URL=sqlite:///./visionid.db

# Face Recognition
SIMILARITY_THRESHOLD=0.6
DETECTION_THRESHOLD=0.5
GPU_ID=0  # -1 for CPU, 0+ for GPU

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🚀 Deployment

### Production Deployment

```bash
# Build production image
docker build -t visionid:prod .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/visionid \
  -v $(pwd)/data:/app/data \
  visionid:prod
```

### Using Docker Compose

```bash
docker-compose -f docker-compose.yml up -d
```

---

## 📊 Performance

- **Detection Speed**: ~50ms per image (GPU)
- **Recognition Speed**: ~20ms per face (GPU)
- **Accuracy**: 99%+ on LFW benchmark
- **Concurrent Requests**: Supports multiple async requests

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **InsightFace** - For the amazing face recognition models
- **FastAPI** - For the excellent web framework

---

## 📧 Contact

**Project Maintainer**: Your Name  
**Email**: your.email@example.com  
**GitHub**: [@yourusername](https://github.com/yourusername)

---

## 🎯 Roadmap

- [x] Phase 1: Project Setup & Structure ✅
- [x] Phase 2: Face Detection & Embedding Implementation ✅
- [x] Phase 3: User Registration System ✅
- [x] Phase 4: Attendance System Implementation ✅
- [x] Phase 5: Testing & Optimization ✅
- [ ] Phase 6: Production Deployment (See DEPLOYMENT.md)

---
