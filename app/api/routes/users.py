import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.domain.models.users import User
from app.domain.schemas.users import (UserCreate, UserPublic, 
                                      UserUpdate, UserUpdateMe, 
                                      UsersPublic, Message, 
                                      UpdatePassword)
from app.domain.services import UserService
from app.core.deps import get_user_service



router = APIRouter(prefix="/users", tags=["users"])

@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(user_service: UserService = Depends(get_user_service), skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    users, count = user_service.get_all_users(skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, user_in: UserCreate, user_service: UserService = Depends(get_user_service)) -> Any:
    """
    Create new user.
    """
    user = user_service.create_user(user_in)
    
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, user_in: UserUpdateMe, current_user: CurrentUser, user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Update own user.
    """
    return user_service.update_user_me(current_user, user_in)


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, password_update: UpdatePassword, current_user: CurrentUser, user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Update own password.
    """
    user_service.update_password(current_user, password_update)
    return Message(message="Password updated successfully")

# @router.post("/signup", response_model=UserPublic)
# def register_user(user_in: UserRegister, user_service: UserService = Depends(get_user_service)) -> Any:
#     """
#     Create new user without the need to be logged in.
#     """
#     return user_service.register_user(user_in)


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    user_service: UserService = Depends(get_user_service)
) -> Any:
    """
    Update a user.
    """
    return user_service.update_user(user_id, user_in)
