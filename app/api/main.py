from fastapi import APIRouter

from app.api.routes import login, private, users


api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
