"""
Database models for users.

This module contains only the SQLModel classes that create database tables.
API schemas are located in app.domain.schemas.users
"""
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from pydantic import EmailStr
import uuid


class User(SQLModel, table=True):
    """
    User database model.
    
    This represents the actual database table for users.
    Contains all fields that are stored in the database.
    """
    __tablename__ = "users"
    
    # Primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        primary_key=True,
        description="Unique identifier for the user"
    )
    
    # User information
    email: EmailStr = Field(
        unique=True, 
        index=True, 
        max_length=255,
        description="User's email address (unique)"
    )
    
    full_name: str | None = Field(
        default=None, 
        max_length=255,
        description="User's full name"
    )
    
    # Authentication
    hashed_password: str = Field(
        description="Bcrypt hashed password"
    )
    
    # User status and permissions
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    
    is_superuser: bool = Field(
        default=False,
        description="Whether the user has superuser privileges"
    )
    
    is_verified: bool = Field(
        default=False,
        description="Whether the user's email has been verified"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the user was created"
    )
    
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the user was last updated"
    )
