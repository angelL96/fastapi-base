"""
Users repository for database operations.

This module contains the repository pattern implementation for user data access.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from uuid import UUID

from app.domain.models.users import User
from app.domain.schemas.users import UserCreate, UserUpdate


class UsersRepository:
    """Repository for user database operations."""
    
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self.session.get(User, user_id)

    def get_active_by_email(self, email: str) -> Optional[User]:
        """Get active user by email address."""
        statement = select(User).where(User.email == email, User.is_active == True)
        return self.session.exec(statement).first()

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        """Create a new user."""
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            is_active=user_create.is_active,
            is_superuser=getattr(user_create, 'is_superuser', False),
            is_verified=False,  # New users start unverified
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update(self, db_user: User, user_update: UserUpdate, hashed_password: Optional[str] = None) -> User:
        """Update an existing user."""
        user_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password update if provided
        if hashed_password:
            user_data["hashed_password"] = hashed_password
        
        # Remove password from update data if it exists (we handle it separately)
        user_data.pop("password", None)
        
        # Update timestamp
        user_data["updated_at"] = datetime.now(timezone.utc)
        
        db_user.sqlmodel_update(user_data)
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        statement = select(User).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def count(self) -> int:
        """Count total number of users."""
        from sqlmodel import func
        statement = select(func.count()).select_from(User)
        return self.session.exec(statement).one()

    def delete(self, user_id: UUID) -> bool:
        """Delete a user by ID."""
        user = self.session.get(User, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def is_email_taken(self, email: str, exclude_user_id: Optional[UUID] = None) -> bool:
        """Check if email is already taken by another user."""
        statement = select(User).where(User.email == email)
        if exclude_user_id:
            statement = statement.where(User.id != exclude_user_id)
        return self.session.exec(statement).first() is not None