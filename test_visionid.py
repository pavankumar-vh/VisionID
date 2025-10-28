"""
VisionID Test Suite
Integration tests for VisionID API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ============= HEALTH CHECK TESTS =============

def test_ping_endpoint():
    """Test the health check endpoint"""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "VisionID API active"
    assert "version" in data


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "VisionID"
    assert data["accuracy"] == "99%+"


# ============= RECOGNITION TESTS =============

def test_recognize_endpoint_exists():
    """Test that recognition endpoint exists"""
    # This will return 422 without file, but endpoint exists
    response = client.post("/api/v1/recognize")
    assert response.status_code == 422  # Missing required file parameter


def test_recognition_history_endpoint():
    """Test recognition history endpoint"""
    response = client.get("/api/v1/recognize/history")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


# ============= REGISTRATION TESTS =============

def test_list_users_endpoint():
    """Test list users endpoint"""
    response = client.get("/api/v1/register/users")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "users" in data


def test_register_endpoint_exists():
    """Test that registration endpoint exists"""
    # This will return 422 without required parameters
    response = client.post("/api/v1/register")
    assert response.status_code == 422


# ============= ATTENDANCE TESTS =============

def test_today_attendance_endpoint():
    """Test today's attendance endpoint"""
    response = client.get("/api/v1/attendance/today")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "date" in data


def test_attendance_statistics_endpoint():
    """Test attendance statistics endpoint"""
    response = client.get("/api/v1/attendance/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_attendance_report_endpoint():
    """Test attendance report endpoint"""
    response = client.get("/api/v1/attendance/report")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


# ============= API DOCUMENTATION TESTS =============

def test_docs_endpoint():
    """Test that API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Test that OpenAPI schema is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "VisionID - AI Face Recognition & Attendance System"


# ============= RUN TESTS =============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
