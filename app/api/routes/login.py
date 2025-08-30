from datetime import timedelta
from typing import Annotated
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from app.core.security import OAuth2PasswordRequestEmail

from app.core.config import settings
from app.domain.services import AuthService
from app.core.deps import get_auth_service

router = APIRouter(tags=["login"])



@router.post("/login/access-token")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestEmail, Depends()],
    auth_service: AuthService = Depends(get_auth_service)
) -> Response:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    
    user = auth_service.login(form_data.email, form_data.password)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user["email"]}, expires_delta=refresh_token_expires
    )
    response = JSONResponse(content={"message": "Login successful"}, status_code=status.HTTP_200_OK)
    # Set the token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=False,    # Only sends cookie over HTTPS
        samesite="lax", # Protects against CSRF
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Cookie expiration in seconds
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=False,    # Only sends cookie over HTTPS
        samesite="lax", # Protects against CSRF
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60  # Cookie expiration in seconds
    )
    
    return response

@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Response:
    

    refresh_token = request.cookies.get("refresh_token")
    user = auth_service.get_current_user(refresh_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )

    response = JSONResponse(content={"message": "Refresh token created successfully"}, status_code=status.HTTP_200_OK)
    # Set the token as an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=True,    # Only sends cookie over HTTPS
        samesite="lax", # Protects against CSRF
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Cookie expiration in seconds
    )
    return response

@router.post("/logout")
async def logout(
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
) -> Response:
    
    auth_service.logout(response)
    
    return JSONResponse(content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK)
