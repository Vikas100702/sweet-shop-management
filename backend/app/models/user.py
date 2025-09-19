"""
User model for authentication and authorization.
Represents users who can login and interact with the sweet shop.
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base

class User(Base):
    """
    User model for storing user information.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)