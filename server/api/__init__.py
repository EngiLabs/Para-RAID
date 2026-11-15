from fastapi import APIRouter
from pydantic import BaseModel

from .command import router as command_router
from .photo import router as photo_router
from .status import router as status_router


api_router = APIRouter()
api_router.include_router(command_router)
api_router.include_router(photo_router)
api_router.include_router(status_router)


class CommandRequest(BaseModel):
    action: str
    direction: str | None = None
    distance_m: float | None = None
    duration_s: float | None = None
    speed: int = 255
    gait: str | None = None
    state: int | bool | None = None
    roll: int = 0
    pitch: int = 0
    yaw: int = 0
    x: float | None = None
    y: float | None = None


__all__ = ("api_router",)
