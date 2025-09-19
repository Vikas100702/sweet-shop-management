"""
Test cases for authentication API endpoints.
Tests user registration and login functionality.
"""
import pytest, os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, get_db
from app.main import app

# Test database setup
DATABASE_URL = os.getenv(
    "DB_URL", 
    "postgresql+psycopg2://sweet_shop:sweet_shop@localhost:5432/sweet_shop"
)
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client

    Base.metadata.drop_all(bind=engine)

def user_registration_success(client):
    """Test successful user registration"""
    response = client.post(
        "/api/auth/register",
        json = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "user_id" in data

def test_user_registration_duplicate_username(client):
    """Test registration with duplicate username fails"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "password123"
        }
    )

    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_user_login_success(client):
    """Test successful user login"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    # Login
    response = client.post(
        "/api/auth/login",
        data = {
            "username": "testuser",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_login_invalid_credentials(client):
    """Test login with invalid credentials fails"""
    response = client.post(
        "api/auth/login",
        data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]