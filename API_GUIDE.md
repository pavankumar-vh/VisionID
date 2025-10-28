# VisionID - API Usage Guide

Complete guide for using VisionID Face Recognition & Attendance System API.

## Table of Contents
- [Authentication](#authentication)
- [Registration APIs](#registration-apis)
- [Recognition APIs](#recognition-apis)
- [Attendance APIs](#attendance-apis)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Code Examples](#code-examples)

---

## Base URL

```
Development: http://localhost:8000
Production: https://yourdomain.com
```

All API endpoints are prefixed with `/api/v1`

---

## Authentication

Currently, the API is open for development. For production deployment, implement API key authentication:

```bash
# Example with API key (when implemented)
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/recognize
```

---

## Registration APIs

### 1. Register New User

Register a new user with face enrollment.

**Endpoint:** `POST /api/v1/register`

**Parameters:**
- `file` (required): Image file containing face (JPG/PNG)
- `name` (required): User's name
- `metadata` (optional): Additional JSON metadata

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "file=@person.jpg" \
  -F "name=John Doe" \
  -F "metadata={\"department\": \"Engineering\"}"
```

**Response:**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "message": "User registered successfully",
  "embedding_size": 512
}
```

**Error Cases:**
- 400: Invalid image, multiple faces, or no face detected
- 409: User with same name already exists
- 500: Server error

---

### 2. List All Users

Get list of all registered users.

**Endpoint:** `GET /api/v1/register/users`

**Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Request:**
```bash
curl "http://localhost:8000/api/v1/register/users?skip=0&limit=10"
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "created_at": "2024-01-15T10:30:00",
      "image_path": "data/embeddings/550e8400.jpg",
      "metadata": "{\"department\": \"Engineering\"}"
    }
  ],
  "total": 1
}
```

---

### 3. Update User

Update user information or face embedding.

**Endpoint:** `PUT /api/v1/register/user/{user_id}`

**Parameters:**
- `user_id` (path): User ID to update
- `name` (optional): New name
- `file` (optional): New face image
- `metadata` (optional): New metadata

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/register/user/{user_id}" \
  -F "name=John Smith" \
  -F "file=@new_photo.jpg"
```

**Response:**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "User updated successfully"
}
```

---

### 4. Delete User

Remove a user from the system.

**Endpoint:** `DELETE /api/v1/register/user/{user_id}`

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/register/user/{user_id}"
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## Recognition APIs

### 1. Recognize Face (Single)

Recognize face(s) in an image.

**Endpoint:** `POST /api/v1/recognize`

**Parameters:**
- `file` (required): Image file containing face(s)

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/recognize" \
  -F "file=@test_image.jpg"
```

**Response:**
```json
{
  "success": true,
  "faces_detected": 2,
  "recognized_faces": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "confidence": 0.87,
      "bbox": [100, 150, 250, 300]
    },
    {
      "user_id": "unknown",
      "name": "Unknown",
      "confidence": 0.0,
      "bbox": [400, 200, 550, 350]
    }
  ],
  "processing_time": 0.234
}
```

---

### 2. Bulk Recognition

Process multiple images concurrently.

**Endpoint:** `POST /api/v1/recognize-bulk`

**Parameters:**
- `files` (required): Multiple image files

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/recognize-bulk" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.jpg"
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "filename": "image1.jpg",
      "faces_detected": 1,
      "recognized": [
        {
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "John Doe",
          "confidence": 0.89
        }
      ]
    },
    {
      "filename": "image2.jpg",
      "faces_detected": 0,
      "recognized": []
    }
  ],
  "statistics": {
    "total_images": 3,
    "total_faces": 5,
    "recognized_faces": 4,
    "processing_time": 1.234
  }
}
```

---

### 3. Recognition History

Get recent recognition history.

**Endpoint:** `GET /api/v1/recognize/history`

**Parameters:**
- `limit` (optional): Maximum records (default: 50)

**Request:**
```bash
curl "http://localhost:8000/api/v1/recognize/history?limit=20"
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "confidence": "0.87",
      "recognized": "true",
      "timestamp": "2024-01-15T14:30:00"
    }
  ],
  "total": 20
}
```

---

## Attendance APIs

### 1. Mark Attendance

Mark attendance by recognizing faces in uploaded image.

**Endpoint:** `POST /api/v1/attendance/mark`

**Parameters:**
- `file` (required): Image containing faces for attendance

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/attendance/mark" \
  -F "file=@class_photo.jpg"
```

**Response:**
```json
{
  "success": true,
  "records": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "timestamp": "2024-01-15T09:00:00",
      "status": "present",
      "confidence": 0.89
    },
    {
      "user_id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Jane Smith",
      "timestamp": "2024-01-15T09:00:00",
      "status": "present",
      "confidence": 0.92
    }
  ],
  "message": "Attendance marked for 2 person(s)"
}
```

---

### 2. Today's Attendance

Get today's attendance records.

**Endpoint:** `GET /api/v1/attendance/today`

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/today"
```

**Response:**
```json
{
  "success": true,
  "date": "2024-01-15",
  "records": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "timestamp": "2024-01-15T09:00:00",
      "status": "present",
      "confidence": 0.89
    }
  ],
  "total_present": 1
}
```

---

### 3. Attendance Report

Generate attendance report for date range.

**Endpoint:** `GET /api/v1/attendance/report`

**Parameters:**
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `user_id` (optional): Filter by user ID

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/report?start_date=2024-01-01&end_date=2024-01-31"
```

**Response:**
```json
{
  "success": true,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "records": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "timestamp": "2024-01-15T09:00:00",
      "status": "present",
      "confidence": 0.89
    }
  ],
  "statistics": {
    "total_days": 31,
    "present_days": 20,
    "absent_days": 11,
    "attendance_rate": 64.52
  },
  "user_statistics": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "present_days": 20,
      "total_days": 31,
      "attendance_rate": 64.52
    }
  ]
}
```

---

### 4. User Attendance History

Get attendance history for specific user.

**Endpoint:** `GET /api/v1/attendance/user/{user_id}`

**Parameters:**
- `user_id` (path): User ID
- `limit` (optional): Maximum records (default: 30)

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/user/{user_id}?limit=10"
```

**Response:**
```json
{
  "success": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "records": [
    {
      "timestamp": "2024-01-15T09:00:00",
      "status": "present",
      "confidence": 0.89
    }
  ],
  "statistics": {
    "total_records": 10,
    "present_count": 8,
    "attendance_rate": 80.0
  }
}
```

---

### 5. Attendance Statistics

Get overall attendance statistics.

**Endpoint:** `GET /api/v1/attendance/statistics`

**Request:**
```bash
curl "http://localhost:8000/api/v1/attendance/statistics"
```

**Response:**
```json
{
  "success": true,
  "total_registered": 50,
  "today_present": 35,
  "today_absent": 15,
  "overall_rate": 78.5,
  "total_attendance_records": 1500,
  "recent_activity": [
    {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "timestamp": "2024-01-15T14:30:00",
      "status": "present"
    }
  ]
}
```

---

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "detail": "Detailed error message"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Common Errors

**1. Invalid Image Format**
```json
{
  "success": false,
  "detail": "Invalid image format. Supported: JPG, PNG"
}
```

**2. No Face Detected**
```json
{
  "success": false,
  "detail": "No face detected in the image"
}
```

**3. Multiple Faces (Registration)**
```json
{
  "success": false,
  "detail": "Please provide image with exactly one face for registration"
}
```

**4. User Not Found**
```json
{
  "success": false,
  "detail": "User not found"
}
```

---

## Code Examples

### Python
```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Register user
def register_user(image_path, name):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'name': name}
        response = requests.post(f"{BASE_URL}/register", files=files, data=data)
        return response.json()

# Recognize faces
def recognize_face(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/recognize", files=files)
        return response.json()

# Mark attendance
def mark_attendance(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/attendance/mark", files=files)
        return response.json()

# Get today's attendance
def get_today_attendance():
    response = requests.get(f"{BASE_URL}/attendance/today")
    return response.json()

# Usage
result = register_user('john.jpg', 'John Doe')
print(result)
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const BASE_URL = 'http://localhost:8000/api/v1';

// Register user
async function registerUser(imagePath, name) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  form.append('name', name);
  
  const response = await axios.post(`${BASE_URL}/register`, form, {
    headers: form.getHeaders()
  });
  return response.data;
}

// Recognize faces
async function recognizeFace(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  
  const response = await axios.post(`${BASE_URL}/recognize`, form, {
    headers: form.getHeaders()
  });
  return response.data;
}

// Mark attendance
async function markAttendance(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  
  const response = await axios.post(`${BASE_URL}/attendance/mark`, form, {
    headers: form.getHeaders()
  });
  return response.data;
}

// Usage
registerUser('john.jpg', 'John Doe')
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### cURL
```bash
# Register user
curl -X POST "http://localhost:8000/api/v1/register" \
  -F "file=@john.jpg" \
  -F "name=John Doe"

# Recognize face
curl -X POST "http://localhost:8000/api/v1/recognize" \
  -F "file=@test.jpg"

# Mark attendance
curl -X POST "http://localhost:8000/api/v1/attendance/mark" \
  -F "file=@class.jpg"

# Get today's attendance
curl "http://localhost:8000/api/v1/attendance/today"

# Get attendance report
curl "http://localhost:8000/api/v1/attendance/report?start_date=2024-01-01&end_date=2024-01-31"
```

---

## Best Practices

1. **Image Quality**: Use high-quality images (minimum 640x480) for better accuracy
2. **Face Size**: Ensure faces are clearly visible (minimum 100x100 pixels)
3. **Lighting**: Good lighting conditions improve recognition accuracy
4. **Single Face Registration**: Always register users with single-face images
5. **Error Handling**: Always check the `success` field in responses
6. **Rate Limiting**: Implement rate limiting in production environments
7. **Batch Processing**: Use bulk recognition for multiple images
8. **Caching**: Cache user lists to reduce database queries

---

## Testing

Use the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/pavankumar-vh/VisionID/issues
- API Documentation: http://localhost:8000/docs
