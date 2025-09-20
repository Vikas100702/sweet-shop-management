"""
Sweet management router for CRUD operations and inventory management.
Handles sweet creation, listing, searching, purchasing, and restocking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.connection import get_db
from app.schemas.sweet import SweetCreate, SweetUpdate, SweetResponse, PurchaseRequest, RestockRequest
from app.models.sweet import Sweet
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/sweets", tags=["Sweets"])

def require_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency to ensure current user is admin.
    Raises 403 if user is not admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.post("/", response_model=SweetResponse, status_code=status.HTTP_201_CREATED)
async def create_sweet(
    sweet_data: SweetCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Create a new sweet (Admin only).
    Adds a new sweet product to the inventory.
    """
    # Check if sweet with same name already exists
    existing_sweet = db.query(Sweet).filter(Sweet.name == sweet_data.name).first()
    if existing_sweet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sweet with this name already exists"
        )
    
    # Create new sweet
    new_sweet = Sweet(**sweet_data.model_dump())
    db.add(new_sweet)
    db.commit()
    db.refresh(new_sweet)
    
    return new_sweet

@router.get("/", response_model=List[SweetResponse])
async def get_sweets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all available sweets.
    Returns all sweets in the system.
    """
    sweets = db.query(Sweet).all()
    return sweets

@router.get("/search", response_model=List[SweetResponse])
async def search_sweets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: Optional[str] = Query(None, description="Search by sweet name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter")
):
    """
    Search for sweets by various criteria.
    Supports filtering by name, category, and price range.
    """
    query = db.query(Sweet)
    
    # Apply filters
    if name:
        query = query.filter(Sweet.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(Sweet.category.ilike(f"%{category}%"))
    
    if min_price is not None:
        query = query.filter(Sweet.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Sweet.price <= max_price)
    
    return query.all()

@router.get("/{sweet_id}", response_model=SweetResponse)
async def get_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific sweet by ID.
    Returns sweet details if found.
    """
    sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    return sweet

@router.put("/{sweet_id}", response_model=SweetResponse)
async def update_sweet(
    sweet_id: int,
    sweet_update: SweetUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Update a sweet's details (Admin only).
    Updates only provided fields, leaves others unchanged.
    """
    sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Update only provided fields
    update_data = sweet_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sweet, field, value)
    
    db.commit()
    db.refresh(sweet)
    return sweet

@router.delete("/{sweet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Delete a sweet (Admin only).
    Removes sweet from inventory permanently.
    """
    sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    db.delete(sweet)
    db.commit()

@router.post("/{sweet_id}/purchase")
async def purchase_sweet(
    sweet_id: int,
    purchase_data: PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Purchase a sweet, reducing its quantity.
    Validates sufficient quantity is available.
    """
    sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Check if sufficient quantity available
    if sweet.quantity < purchase_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient quantity. Available: {sweet.quantity}, Requested: {purchase_data.quantity}"
        )
    
    # Reduce quantity
    sweet.quantity -= purchase_data.quantity
    db.commit()
    db.refresh(sweet)
    
    return {
        "message": "Purchase successful",
        "purchased_quantity": purchase_data.quantity,
        "remaining_quantity": sweet.quantity,
        "total_cost": purchase_data.quantity * sweet.price
    }

@router.post("/{sweet_id}/restock")
async def restock_sweet(
    sweet_id: int,
    restock_data: RestockRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Restock a sweet, increasing its quantity (Admin only).
    Adds specified quantity to current stock.
    """
    sweet = db.query(Sweet).filter(Sweet.id == sweet_id).first()
    if not sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Validate restock quantity is positive
    if restock_data.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restock quantity must be positive"
        )
    
    # Increase quantity
    old_quantity = sweet.quantity
    sweet.quantity += restock_data.quantity
    db.commit()
    db.refresh(sweet)
    
    return {
        "message": "Restock successful",
        "restocked_quantity": restock_data.quantity,
        "previous_quantity": old_quantity,
        "new_quantity": sweet.quantity
    }