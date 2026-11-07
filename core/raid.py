from __future__ import annotations

from json import dumps as json_dumps
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class Raid:
    def __init__(self) -> None:
        self._ws: WebSocket | None = None

    def bind(self, ws: WebSocket) -> None:
        self._ws = ws

    def unbind(self) -> None:
        self._ws = None

    @property
    def is_connected(self) -> bool:
        return self._ws is not None

    async def send_command(self, command: str, payload: dict[str, Any] | None = None) -> bool:
        if not self._ws:
            logger.warning("cen't send command '%s': no WS connection", command)
            return False
        message = {
            "type": "command",
            "command": command,
            "payload": payload or {},
        }
        try:
            await self._ws.send_text(json_dumps(message))
            return True
        except:
            logger.exception("failed to send command '%s'", command)
            return False

    async def move(self, direction: str) -> bool:
        return await self.send_command("move", {"direction": direction})

    async def stop(self) -> bool:
        return await self.send_command("stop")

    async def set_gait(self, gait: str) -> bool:
        return await self.send_command("set_gait", {"gait": gait})

    async def request_telemetry(self) -> bool:
        return await self.send_command("request_telemetry")

    async def set_led(self, state: bool) -> bool:
        return await self.send_command("set_led", {"state": state})

    async def home(self) -> bool:
        return await self.send_command("home")

    async def capture_photo(self) -> bool:
        return await self.send_command("capture_photo")

    async def navigate_to(self, x: float, y: float) -> bool:
        return await self.send_command("navigate_to", {"x": x, "y": y})


raid = Raid()
