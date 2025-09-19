"""
Test cases for authentication service.
Tests password hashing, token generation, and user verification.
"""
import pytest
from app.services.auth_service import AuthService, verify_password, get_password_hash, create_access_token, verify_token

def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hashed password should not equal original
    assert hashed != password
    
    # Should be able to verify correct password
    assert verify_password(password, hashed) is True
    
    # Should fail with wrong password
    assert verify_password("wrongpassword", hashed) is False

def test_access_token_creation():
    """Test JWT access token creation and verification"""
    user_data = {"sub": "testuser", "user_id": 1}
    token = create_access_token(data=user_data)
    
    # Token should be created
    assert token is not None
    assert isinstance(token, str)
    
    # Should be able to verify token
    payload = verify_token(token)
    assert payload["sub"] == "testuser"
    assert payload["user_id"] == 1

def test_invalid_token_verification():
    """Test that invalid tokens are rejected"""
    invalid_token = "invalid.jwt.token"
    payload = verify_token(invalid_token)
    assert payload is None