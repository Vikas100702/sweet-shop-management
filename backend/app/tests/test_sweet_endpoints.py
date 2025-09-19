"""
Test cases for sweet management API endpoints.
Tests CRUD operations and inventory management.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sweets.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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
    """Create test client with clean database"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Register and login user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client):
    """Create authenticated admin user and return auth headers"""
    # Register admin user (we'll need to make them admin manually)
    client.post(
        "/api/auth/register",
        json={"username": "admin", "email": "admin@example.com", "password": "admin123"}
    )
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    
    # Make user admin (direct database manipulation for testing)
    from app.models.user import User
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == "admin").first()
    user.is_admin = True
    db.commit()
    db.close()
    
    return {"Authorization": f"Bearer {token}"}

def test_create_sweet_success(client, admin_headers):
    """Test successful sweet creation by admin"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.99,
            "quantity": 100
        },
        headers=admin_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chocolate Bar"
    assert data["price"] == 2.99

def test_create_sweet_unauthorized(client, auth_headers):
    """Test that non-admin users cannot create sweets"""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Candy",
            "category": "Hard",
            "price": 1.99,
            "quantity": 50
        },
        headers=auth_headers
    )
    assert response.status_code == 403

def test_get_sweets_list(client, auth_headers, admin_headers):
    """Test retrieving list of all sweets"""
    # Create some sweets first
    client.post(
        "/api/sweets",
        json={"name": "Gummy Bears", "category": "Gummy", "price": 3.99, "quantity": 75},
        headers=admin_headers
    )
    client.post(
        "/api/sweets",
        json={"name": "Lollipop", "category": "Hard", "price": 1.50, "quantity": 200},
        headers=admin_headers
    )
    
    # Get sweets list
    response = client.get("/api/sweets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(sweet["name"] == "Gummy Bears" for sweet in data)
    assert any(sweet["name"] == "Lollipop" for sweet in data)

def test_search_sweets_by_name(client, auth_headers, admin_headers):
    """Test searching sweets by name"""
    # Create test sweets
    client.post(
        "/api/sweets",
        json={"name": "Dark Chocolate", "category": "Chocolate", "price": 4.99, "quantity": 30},
        headers=admin_headers
    )
    client.post(
        "/api/sweets",
        json={"name": "Milk Chocolate", "category": "Chocolate", "price": 3.99, "quantity": 50},
        headers=admin_headers
    )
    
    # Search for chocolate
    response = client.get("/api/sweets/search?name=chocolate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("chocolate" in sweet["name"].lower() for sweet in data)

def test_search_sweets_by_category(client, auth_headers, admin_headers):
    """Test searching sweets by category"""
    # Create test sweets
    client.post(
        "/api/sweets",
        json={"name": "Gummy Worms", "category": "Gummy", "price": 2.99, "quantity": 60},
        headers=admin_headers
    )
    client.post(
        "/api/sweets",
        json={"name": "Chocolate Bar", "category": "Chocolate", "price": 3.99, "quantity": 40},
        headers=admin_headers
    )
    
    # Search by category
    response = client.get("/api/sweets/search?category=Gummy", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Gummy"

def test_purchase_sweet_success(client, auth_headers, admin_headers):
    """Test successful sweet purchase"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "Candy Cane", "category": "Hard", "price": 1.99, "quantity": 10},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Purchase sweet
    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        json={"quantity": 2},
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Check quantity was reduced
    get_response = client.get("/api/sweets", headers=auth_headers)
    sweet = next(s for s in get_response.json() if s["id"] == sweet_id)
    assert sweet["quantity"] == 8

def test_purchase_sweet_insufficient_quantity(client, auth_headers, admin_headers):
    """Test purchase with insufficient quantity fails"""
    # Create sweet with low quantity
    create_response = client.post(
        "/api/sweets",
        json={"name": "Rare Candy", "category": "Special", "price": 9.99, "quantity": 2},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Try to purchase more than available
    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        json={"quantity": 5},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "insufficient quantity" in response.json()["detail"].lower()

def test_restock_sweet_success(client, admin_headers):
    """Test successful sweet restocking by admin"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "Jelly Beans", "category": "Jelly", "price": 2.50, "quantity": 5},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Restock sweet
    response = client.post(
        f"/api/sweets/{sweet_id}/restock",
        json={"quantity": 20},
        headers=admin_headers
    )
    assert response.status_code == 200
    
    # Check quantity was increased
    get_response = client.get("/api/sweets", headers=admin_headers)
    sweet = next(s for s in get_response.json() if s["id"] == sweet_id)
    assert sweet["quantity"] == 25

def test_restock_sweet_unauthorized(client, auth_headers, admin_headers):
    """Test that non-admin users cannot restock"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "Sour Patch", "category": "Sour", "price": 3.50, "quantity": 10},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Try to restock as regular user
    response = client.post(
        f"/api/sweets/{sweet_id}/restock",
        json={"quantity": 10},
        headers=auth_headers
    )
    assert response.status_code == 403

def test_update_sweet_success(client, admin_headers):
    """Test successful sweet update by admin"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "Old Name", "category": "Test", "price": 1.00, "quantity": 1},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Update sweet
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json={"name": "New Name", "price": 2.00},
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == 2.00
    assert data["category"] == "Test"  # Should remain unchanged

def test_delete_sweet_success(client, admin_headers):
    """Test successful sweet deletion by admin"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "To Delete", "category": "Test", "price": 1.00, "quantity": 1},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Delete sweet
    response = client.delete(f"/api/sweets/{sweet_id}", headers=admin_headers)
    assert response.status_code == 204
    
    # Verify sweet is deleted
    get_response = client.get("/api/sweets", headers=admin_headers)
    assert not any(s["id"] == sweet_id for s in get_response.json())

def test_delete_sweet_unauthorized(client, auth_headers, admin_headers):
    """Test that non-admin users cannot delete sweets"""
    # Create sweet first
    create_response = client.post(
        "/api/sweets",
        json={"name": "Protected", "category": "Test", "price": 1.00, "quantity": 1},
        headers=admin_headers
    )
    sweet_id = create_response.json()["id"]
    
    # Try to delete as regular user
    response = client.delete(f"/api/sweets/{sweet_id}", headers=auth_headers)
    assert response.status_code == 403