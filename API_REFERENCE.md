# VisionID API Quick Reference

## Base URL
```
http://localhost:8000
```

---

## 🏥 Health & Info Endpoints

### Get API Status
```http
GET /ping
```

**Response:**
```json
{
  "status": "VisionID API active",
  "version": "1.0.0",
  "message": "AI Face Recognition System is operational"
}
```

### Get API Info
```http
GET /
```

---

## 👤 Registration Endpoints

### Register New User
```http
POST /api/v1/register
Content-Type: multipart/form-data

name: "John Doe"
file: [image file]
metadata: {"department": "Engineering"} (optional)
```

### List All Users
```http
GET /api/v1/register/users?limit=100&offset=0
```

### Update User
```http
PUT /api/v1/register/user/{user_id}
Content-Type: multipart/form-data

name: "Jane Doe" (optional)
file: [new image file] (optional)
```

### Delete User
```http
DELETE /api/v1/register/user/{user_id}
```

---

## 🔍 Recognition Endpoints

### Recognize Faces in Image
```http
POST /api/v1/recognize
Content-Type: multipart/form-data

file: [image file]
```

**Response:**
```json
{
  "success": true,
  "detected_faces": 2,
  "recognitions": [
    {
      "user_id": "123",
      "name": "John Doe",
      "confidence": 0.95,
      "bbox": [100, 100, 200, 200]
    }
  ],
  "message": "Recognition complete"
}
```

### Recognize Video Frame
```http
POST /api/v1/recognize/video
Content-Type: multipart/form-data

file: [video frame image]
```

### Get Recognition History
```http
GET /api/v1/recognize/history?limit=50
```

---

## 📅 Attendance Endpoints

### Mark Attendance
```http
POST /api/v1/attendance/mark
Content-Type: multipart/form-data

file: [image file with faces]
```

**Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_id": "123",
      "name": "John Doe",
      "timestamp": "2025-10-28T10:30:00",
      "status": "present"
    }
  ],
  "message": "Attendance marked successfully"
}
```

### Get Today's Attendance
```http
GET /api/v1/attendance/today
```

**Response:**
```json
{
  "success": true,
  "date": "2025-10-28",
  "records": [...],
  "total_present": 25,
  "message": "Today's attendance retrieved"
}
```

### Get Attendance Report
```http
GET /api/v1/attendance/report?start_date=2025-10-01&end_date=2025-10-28&user_id=123
```

**Response:**
```json
{
  "success": true,
  "start_date": "2025-10-01",
  "end_date": "2025-10-28",
  "records": [...],
  "statistics": {
    "total_days": 28,
    "present_days": 22,
    "absent_days": 6,
    "attendance_rate": 78.57
  }
}
```

### Get User Attendance History
```http
GET /api/v1/attendance/user/{user_id}?limit=30
```

### Get Attendance Statistics
```http
GET /api/v1/attendance/statistics
```

**Response:**
```json
{
  "success": true,
  "total_registered": 50,
  "today_present": 35,
  "today_absent": 15,
  "overall_rate": 85.5
}
```

---

## 📖 Documentation Endpoints

### Swagger UI (Interactive)
```
http://localhost:8000/docs
```

### ReDoc (Alternative)
```
http://localhost:8000/redoc
```

### OpenAPI Schema (JSON)
```http
GET /openapi.json
```

---

## 🔧 cURL Examples

### Health Check
```bash
curl http://localhost:8000/ping
```

### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "name=John Doe" \
  -F "file=@/path/to/photo.jpg"
```

### Recognize Faces
```bash
curl -X POST "http://localhost:8000/api/v1/recognize" \
  -F "file=@/path/to/image.jpg"
```

### Mark Attendance
```bash
curl -X POST "http://localhost:8000/api/v1/attendance/mark" \
  -F "file=@/path/to/group_photo.jpg"
```

### Get Today's Attendance
```bash
curl http://localhost:8000/api/v1/attendance/today
```

---

## 🐍 Python Examples

### Using requests library

```python
import requests

# Health Check
response = requests.get("http://localhost:8000/ping")
print(response.json())

# Register User
with open("photo.jpg", "rb") as f:
    files = {"file": f}
    data = {"name": "John Doe"}
    response = requests.post(
        "http://localhost:8000/api/v1/register",
        files=files,
        data=data
    )
print(response.json())

# Recognize Faces
with open("image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        "http://localhost:8000/api/v1/recognize",
        files=files
    )
print(response.json())
```

### Using httpx (async)

```python
import httpx
import asyncio

async def recognize_face():
    async with httpx.AsyncClient() as client:
        with open("image.jpg", "rb") as f:
            files = {"file": f}
            response = await client.post(
                "http://localhost:8000/api/v1/recognize",
                files=files
            )
        return response.json()

# Run async function
result = asyncio.run(recognize_face())
print(result)
```

---

## 📝 Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

---

## 🔒 Authentication (Future)

Currently, the API is open. In production, add authentication:

```http
Authorization: Bearer <token>
```

Or use API Key:

```http
X-API-Key: your-api-key-here
```

---

## 📊 Rate Limiting (Future)

Future implementation will include:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## 🌐 CORS

Currently allows all origins (`*`). In production, configure specific origins in `app/main.py`:

```python
allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"]
```

---

For complete documentation, visit: **http://localhost:8000/docs**
