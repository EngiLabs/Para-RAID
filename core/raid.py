from __future__ import annotations

import asyncio
from json import dumps as json_dumps
import logging
from typing import Any

from config import DEFAULT_SPEED_MPS, DIRECTION_ID_MAP, GAIT_MAP

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class Raid:
    def __init__(self) -> None:
        self._ws: WebSocket | None = None
        self._move_task: asyncio.Task | None = None

    def bind(self, ws: WebSocket) -> None:
        self._ws = ws
        logger.info("Raid WS client bound")

    def unbind(self) -> None:
        self._ws = None
        self._cancel_move_task()
        logger.info("Raid WS client unbound")

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

    def _cancel_move_task(self) -> None:
        if self._move_task and not self._move_task.done():
            self._move_task.cancel()
        self._move_task = None

    async def send_command(self, command: str, payload: dict[str, Any] | None = None) -> bool:
        if not self._ws:
            logger.warning("can't send command '%s': no WS connection", command)
            return False
        message = {
            "type": "command",
            "action": command,
            "params": payload or {},
        }
        try:
            raw_data = json_dumps(message)
            await self._ws.send_text(raw_data)
            logger.debug("sent command: '%s' with data %s", command, raw_data)
            return True
        except:
            logger.exception("failed to send command '%s'", command)
            return False

    async def send_photo_request(self) -> bool:
        if not self._ws:
            logger.warning("can't send photo request: no WS connection")
            return False
        message = {
            "type": "photo_request"
        }
        try:
            payload = json_dumps(message)
            await self._ws.send_text(payload)
            logger.debug("sent photo request: '%s'", payload)
            return True
        except:
            logger.exception("failed to send photo request")
            return False

    async def move(self, direction: str, speed: int = 255) -> bool:
        self._cancel_move_task()
        direction_id = DIRECTION_ID_MAP.get(direction.lower(), 1)
        payload = {
            "direction": direction_id,
            "speed": speed,
        }
        return await self.send_command("move", payload)

    async def move_timed(self,
        direction: str,
        distance_m: float | None = None,
        duration_s: float | None = None,
        speed: int = 255,
    ) -> dict[str, Any]:
        self._cancel_move_task()

        calc_duration = None
        if duration_s is not None and duration_s > 0:
            calc_duration = duration_s
        elif distance_m is not None and distance_m > 0:
            speed_ratio = max(1, min(255, speed)) / 255.0
            actual_mps = DEFAULT_SPEED_MPS * speed_ratio
            calc_duration = distance_m / actual_mps

        success = await self.move(direction, speed)
        if not success:
            return {"status": "error", "detail": "failed to send move command to robot"}

        if calc_duration is not None and calc_duration > 0:
            async def _timed_stop(wait_sec: float) -> None:
                try:
                    await asyncio.sleep(wait_sec)
                    await self.stop()
                    logger.info("timed movement (%s) completed after %.2fs", direction, wait_sec)
                except asyncio.CancelledError:
                    pass

            self._move_task = asyncio.create_task(_timed_stop(calc_duration))
            return {
                "status": "ok",
                "direction": direction,
                "duration_s": round(calc_duration, 2),
                "distance_m": distance_m,
                "timed": True,
            }

        return {
            "status": "ok",
            "direction": direction,
            "timed": False,
        }

    async def stop(self) -> bool:
        self._cancel_move_task()
        return await self.send_command("stop")

    async def set_gait(self, gait: str) -> bool:
        gait_id = GAIT_MAP.get(gait.lower(), 0)
        return await self.send_command("set_gait", {"gait_id": gait_id})

    async def set_pose(self, angles: list[float]) -> bool:
        if len(angles) != 12:
            raise ValueError(f"set_pose requires 12 angles, got {len(angles)}")
        return await self.send_command("set_pose", {"angles": [float(a) for a in angles]})

    async def request_telemetry(self) -> bool:
        return await self.send_command("telemetry")

    async def set_led(self, state: bool) -> bool:
        return await self.send_command("set_led", {"state": state})

    async def home(self) -> bool:
        self._cancel_move_task()
        return await self.send_command("home")

    async def relax(self) -> bool:
        self._cancel_move_task()
        return await self.send_command("relax")

    async def wake(self) -> bool:
        return await self.send_command("wake")

    async def capture_photo(self) -> bool:
        return await self.send_photo_request()

    async def navigate_to(self, x: float, y: float) -> bool:
        return await self.send_command("navigate_to", {"x": x, "y": y})


raid = Raid()
