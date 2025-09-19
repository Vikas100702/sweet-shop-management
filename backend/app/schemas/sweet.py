"""
Pydantic schemas for sweet-related API requests and responses.
"""
from pydantic import BaseModel
from typing import Optional

class SweetBase(BaseModel):
    """Base schema with common sweet fields"""
    name: str
    category: str
    price: float
    quantity: int

class SweetCreate(SweetBase):
    """Schema for creating a new sweet"""
    pass

class SweetUpdate(BaseModel):
    """Schema for updating a sweet (all fields optional)"""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

class SweetResponse(SweetBase):
    """Schema for sweet data response"""
    id: int
    
    class Config:
        from_attributes = True

class PurchaseRequest(BaseModel):
    """Schema for purchase request"""
    quantity: int = 1

class RestockRequest(BaseModel):
    """Schema for restock request"""
    quantity: int