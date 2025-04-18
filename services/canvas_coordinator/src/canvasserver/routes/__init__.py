from fastapi import APIRouter

from .actions import router as action_router
from .displays import router as display_router
from .images import router as image_router
from .prompts import router as prompt_router
from .push_frames import router as push_frames_router

api_router = APIRouter()
api_router.include_router(action_router)
api_router.include_router(display_router)
api_router.include_router(image_router)
api_router.include_router(prompt_router)
api_router.include_router(push_frames_router)
