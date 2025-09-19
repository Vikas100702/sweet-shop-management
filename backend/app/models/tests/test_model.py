import pytest, os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.models.user import User
from app.models.sweet import Sweet

# Test database setup
DATABASE_URL = os.getenv(
    "DB_URL", 
    "postgresql+psycopg2://sweet_shop:sweet_shop@localhost:5432/sweet_shop"
)
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_user_creation(db_session):
    """Test user model creation and attributes"""
    user = User(
        username = "testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    # Test user was created successfully
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_admin is False

def test_sweet_creation(db_session):
    """Test sweet model creation and attributes"""
    sweet = Sweet(
        name="Chocolate Cake",
        category="Chocolate",
        price=15.99,
        quantity=10
    )
    db_session.add(sweet)
    db_session.commit()

    # Test sweet was created successfully
    assert sweet.id is not None
    assert sweet.name == "Chocolate Cake"
    assert sweet.category == "Chocolate"
    assert sweet.price == 15.99
    assert sweet.quantity == 10

def test_sweet_purchase_quantity_reduction(db_session):
    """Test that purchasing reduces quantity"""
    sweet = Sweet(name="Gummy Bears", category="Gummy", price=1.50, quantity=50)
    db_session.add(sweet)
    db_session.commit()
    
    # Simulate purchase
    original_quantity = sweet.quantity
    sweet.quantity -= 1
    db_session.commit()
    
    assert sweet.quantity == original_quantity - 1