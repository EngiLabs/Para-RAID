from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from core import raid, state_snapshot
from typing import Any


class CommandRequest(BaseModel):
    action: str
    direction: str | None = None
    distance_m: float | None = None
    duration_s: float | None = None
    speed: int = 255
    gait: str | None = None
    state: int | bool | None = None
    angles: list[float] | None = None
    x: float | None = None
    y: float | None = None


router = APIRouter()


@router.post("/command")
async def post_command(cmd: CommandRequest) -> dict[str, Any]:
    action = cmd.action.lower()

    if action in ("forward", "backward", "left", "right", "move"):
        direction = cmd.direction or action
        if direction == "move":
            direction = "forward"
        res = await raid.move_timed(
            direction=direction,
            distance_m=cmd.distance_m,
            duration_s=cmd.duration_s,
            speed=cmd.speed,
        )
        return res

    elif action in ("stop", "estop"):
        ok = await raid.stop()
        return {"status": "ok" if ok else "error", "action": "stop"}

    elif action in ("gait", "set_gait"):
        gait_name = cmd.gait or "walk"
        ok = await raid.set_gait(gait_name)
        if ok:
            state_snapshot.current_gait = gait_name
        return {"status": "ok" if ok else "error", "action": "set_gait", "gait": gait_name}

    elif action == "home":
        ok = await raid.home()
        return {"status": "ok" if ok else "error", "action": "home"}

    elif action == "relax":
        ok = await raid.relax()
        return {"status": "ok" if ok else "error", "action": "relax"}

    elif action == "wake":
        ok = await raid.wake()
        return {"status": "ok" if ok else "error", "action": "wake"}

    elif action in ("pose", "set_pose"):
        if not cmd.angles or len(cmd.angles) != 12:
            raise HTTPException(
                status_code=400,
                detail="12 servo angles (RF, LF, RB, LB × [phi, alpha, beta] in degrees) are required for set_pose",
            )
        ok = await raid.set_pose(cmd.angles)
        return {"status": "ok" if ok else "error", "action": "set_pose", "angles": cmd.angles}

    elif action in ("led", "set_led"):
        val = 1 if cmd.state else 0
        ok = await raid.set_led(val)
        return {"status": "ok" if ok else "error", "action": "set_led", "state": val}

    elif action in ("photo", "capture_photo"):
        ok = await raid.capture_photo()
        return {"status": "ok" if ok else "error", "action": "photo_request"}

    elif action in ("goto", "navigate_to"):
        if cmd.x is None or cmd.y is None:
            raise HTTPException(status_code=400, detail="x and y coordinates are required for navigation")
        ok = await raid.navigate_to(cmd.x, cmd.y)
        return {"status": "ok" if ok else "error", "action": "navigate_to", "target": {"x": cmd.x, "y": cmd.y}}

    elif action in ("status", "telemetry"):
        await raid.request_telemetry()
        return {"status": "ok", "snapshot": state_snapshot.to_dict()}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: '{action}'")
