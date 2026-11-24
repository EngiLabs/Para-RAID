from fastapi import APIRouter
from core import state_snapshot
from typing import Any


router = APIRouter()


@router.get("/status")
async def get_status() -> dict[str, Any]:
    data = state_snapshot.to_dict()
    data["formatted_status"] = state_snapshot.format_server_status()
    data["formatted_telemetry"] = state_snapshot.format_telemetry()
    data["formatted"] = state_snapshot.format_status()
    return data
