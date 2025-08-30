"""
User service for business logic.

This module contains the service layer for user-related business operations.
It coordinates between repositories and handles business rules.
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException

from app.core.security import get_password_hash, verify_password
from app.domain.models.users import User
from app.domain.schemas.users import UserCreate, UserUpdate, UserRegister, UserUpdateMe, UpdatePassword
from app.domain.repositories import UsersRepository


class UserService:
    """Service for user business logic."""
    
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user."""
        # Check if email already exists
        if self.user_repository.get_by_email(user_create.email):
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system."
            )
        
        # Hash the password
        hashed_password = get_password_hash(user_create.password)
        
        # Create the user
        return self.user_repository.create(user_create, hashed_password)

    def register_user(self, user_register: UserRegister) -> User:
        """Register a new user (public registration)."""
        # Check if email already exists
        if self.user_repository.get_by_email(user_register.email):
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system"
            )
        
        # Convert to UserCreate (with default values for registration)
        user_create = UserCreate(
            email=user_register.email,
            password=user_register.password,
            full_name=user_register.full_name,
            is_active=True,  # New registrations are active by default
            is_superuser=False  # New registrations are never superusers
        )
        
        return self.create_user(user_create)

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.user_repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repository.get_by_email(email)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Get all users with pagination."""
        users = self.user_repository.get_all(skip=skip, limit=limit)
        count = self.user_repository.count()
        return users, count

    def update_user(self, user_id: UUID, user_update: UserUpdate) -> User:
        """Update a user (admin operation)."""
        # Get the user
        db_user = self.user_repository.get_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=404,
                detail="The user with this id does not exist in the system"
            )
        
        # Check if email is being changed and if it's already taken
        if user_update.email and user_update.email != db_user.email:
            if self.user_repository.is_email_taken(user_update.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )
        
        # Hash password if provided
        hashed_password = None
        if user_update.password:
            hashed_password = get_password_hash(user_update.password)
        
        return self.user_repository.update(db_user, user_update, hashed_password)

    def update_user_me(self, current_user: User, user_update: UserUpdateMe) -> User:
        """Update current user's own profile."""
        # Check if email is being changed and if it's already taken
        if user_update.email and user_update.email != current_user.email:
            if self.user_repository.is_email_taken(user_update.email, exclude_user_id=current_user.id):
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )
        
        # Convert UserUpdateMe to UserUpdate (limited fields)
        user_update_data = UserUpdate(
            email=user_update.email,
            full_name=user_update.full_name,
            # Don't allow users to change their own active/superuser status
            is_active=None,
            is_superuser=None,
            is_verified=None,
            password=None
        )
        
        return self.user_repository.update(current_user, user_update_data)

    def update_password(self, current_user: User, password_update: UpdatePassword) -> User:
        """Update user's password."""
        # Verify current password
        if not verify_password(password_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=400,
                detail="Incorrect current password"
            )
        
        # Hash new password
        hashed_password = get_password_hash(password_update.new_password)
        
        # Update password
        user_update = UserUpdate(password=None)  # We handle password separately
        return self.user_repository.update(current_user, user_update, hashed_password)

    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""
        if not self.user_repository.get_by_id(user_id):
            raise HTTPException(
                status_code=404,
                detail="The user with this id does not exist in the system"
            )
        
        return self.user_repository.delete(user_id)

    def is_email_available(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if email is available for use."""
        return not self.user_repository.is_email_taken(email, exclude_user_id)
