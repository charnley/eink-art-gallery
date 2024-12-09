from fastapi import APIRouter

from .images import router

api_router = APIRouter()
api_router.include_router(router)
