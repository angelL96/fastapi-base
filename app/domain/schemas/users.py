"""
User schemas for API requests and responses.

These are Pydantic models used for API validation and serialization.
They do not create database tables.
"""
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, ConfigDict
import uuid
from datetime import datetime


class UserBase(SQLModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(max_length=255, description="User's email address")
    full_name: str | None = Field(default=None, max_length=255, description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user is active")


# Schemas for API requests (input)

class UserCreate(UserBase):
    """Schema for creating a new user (admin only)."""
    password: str = Field(
        min_length=8, 
        max_length=128,
        description="Plain text password (will be hashed)"
    )
    is_superuser: bool = Field(default=False, description="Grant superuser privileges")


class UserRegister(SQLModel):
    """Schema for user self-registration."""
    email: EmailStr = Field(max_length=255, description="User's email address")
    password: str = Field(
        min_length=8, 
        max_length=128,
        description="Plain text password (will be hashed)"
    )
    full_name: str | None = Field(default=None, max_length=255, description="User's full name")


class UserUpdate(SQLModel):
    """Schema for updating user information (admin only)."""
    email: EmailStr | None = Field(default=None, max_length=255, description="New email address")
    full_name: str | None = Field(default=None, max_length=255, description="New full name")
    password: str | None = Field(
        default=None, 
        min_length=8, 
        max_length=128,
        description="New password (will be hashed)"
    )
    is_active: bool | None = Field(default=None, description="Update active status")
    is_superuser: bool | None = Field(default=None, description="Update superuser status")
    is_verified: bool | None = Field(default=None, description="Update verified status")


class UserUpdateMe(SQLModel):
    """Schema for users updating their own profile."""
    full_name: str | None = Field(default=None, max_length=255, description="New full name")
    email: EmailStr | None = Field(default=None, max_length=255, description="New email address")


class UpdatePassword(SQLModel):
    """Schema for password change requests."""
    current_password: str = Field(
        min_length=8, 
        max_length=128,
        description="Current password for verification"
    )
    new_password: str = Field(
        min_length=8, 
        max_length=128,
        description="New password"
    )


# Schemas for API responses (output)

class UserPublic(UserBase):
    """Public user information returned by API."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID = Field(description="Unique user identifier")
    is_superuser: bool = Field(description="Whether user has superuser privileges")
    is_verified: bool = Field(description="Whether user's email is verified")
    created_at: datetime = Field(description="When the user was created")


class UserPublicWithTimestamps(UserPublic):
    """Extended user information with all timestamps."""
    updated_at: datetime = Field(description="When the user was last updated")


class UsersPublic(SQLModel):
    """Response schema for paginated user lists."""
    data: list[UserPublic] = Field(description="List of users")
    count: int = Field(description="Total number of users")


# Authentication related schemas

class UserInDB(UserBase):
    """User schema as stored in database (for internal use)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    hashed_password: str
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class Message(SQLModel):
    """General message response schema."""
    message: str = Field(description="Response message")
