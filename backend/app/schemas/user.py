"""
Pydantic schemas for user-related API requests and responses.
Defines data validation and serialization models.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    """Schema for user registration request"""
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login request"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Schema for user data response"""
    id: int
    username: str
    email: str
    is_admin: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None