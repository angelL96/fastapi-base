from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.domain.models.users import User, UserPublic
from app.domain.services.auth_service import AuthService
from app.domain.repositories.users_repository import UsersRepository

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(UsersRepository(session))
@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep, auth_service: AuthService = Depends(get_auth_service)) -> Any:
    """
    Create a new user.
    """

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=auth_service.get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()

    return user
