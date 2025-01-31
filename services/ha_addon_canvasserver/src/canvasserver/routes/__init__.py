from fastapi import APIRouter

from .actions import router as action_router
from .images import router as image_router
from .prompts import router as prompt_router

api_router = APIRouter()
api_router.include_router(image_router)
api_router.include_router(prompt_router)
api_router.include_router(action_router)
