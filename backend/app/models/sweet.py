"""
Sweet model for managing candy inventory.
Represents individual sweet products in the shop.
"""

from sqlalchemy import Column, Integer, String, Float
from app.database.connection import Base

class Sweet(Base):
    """
    Sweet model for storing sweet/candy information.
    """

    __tablename__ = "sweets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)