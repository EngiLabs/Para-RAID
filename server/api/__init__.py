from fastapi import APIRouter

from .command import router as command_router
from .photo import router as photo_router
from .status import router as status_router


api_router = APIRouter()
api_router.include_router(command_router)
api_router.include_router(photo_router)
api_router.include_router(status_router)


__all__ = ("api_router",)
