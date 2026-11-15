from fastapi import APIRouter
from core import state_snapshot
from typing import Any


router = APIRouter()


@router.get("/status")
async def get_status() -> dict[str, Any]:
    return state_snapshot.to_dict()
