from app.domain.repositories.users_repository import UsersRepository
from fastapi import HTTPException, status
from typing import Annotated, Any
from fastapi import Depends
from app.core.deps import SessionDep
from app.core.security import OAuth2PasswordBearerWithCookie
from app.domain.models.users import User
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_V1_STR}/login/access-token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    email: str | None = None

class AuthService:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    def login(self, email: str, password: str) -> str:
        #user = self.users_repository.get_user_by_email(email)
        user = {
            "email": email,
            "hashed_password": "$2a$12$NhJacd8aMqce.C2SWmMfuOwQgxSQ52O25HTgfHH6myiqpPmSp.B9i"
        }
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not self.verify_password(password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user

    def get_current_user(self,
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(email=email)
        except InvalidTokenError:
            raise credentials_exception
        
        if token_data.email is None:
            raise credentials_exception
        
        user = self.users_repository.get_by_email(token_data.email)
        
        if user is None:
            raise credentials_exception
        
        return user
    
    def create_access_token(self, subject: str | Any, expires_delta: timedelta) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        return self.create_access_token(data=data, expires_delta=expires_delta)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)