from __future__ import annotations

import logging
import time
from typing import Any
import httpx

import config as global_config


logger = logging.getLogger(__name__)


class RaidAPIClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self._base_url = (base_url or global_config.RAID_API_URL).rstrip("/")
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def send_command(self, action: str, **payload: Any) -> dict[str, Any] | None:
        client = self._get_client()
        body = {"action": action, **{k: v for k, v in payload.items() if v is not None}}
        try:
            resp = await client.post("/api/command", json=body)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("RaidAPI command '%s' failed: %s", action, exc)
            return None

    async def move(
        self,
        direction: str,
        distance_m: float | None = None,
        duration_s: float | None = None,
        speed: int = 255,
    ) -> bool:
        res = await self.send_command(
            direction,
            direction=direction,
            distance_m=distance_m,
            duration_s=duration_s,
            speed=speed,
        )
        return bool(res and res.get("status") == "ok")

    async def stop(self) -> bool:
        res = await self.send_command("stop")
        return bool(res and res.get("status") == "ok")

    async def home(self) -> bool:
        res = await self.send_command("home")
        return bool(res and res.get("status") == "ok")

    async def navigate_to(self, x: float, y: float) -> bool:
        res = await self.send_command("goto", x=x, y=y)
        return bool(res and res.get("status") == "ok")

    async def get_status(self) -> dict[str, Any] | None:
        client = self._get_client()
        try:
            t0 = time.monotonic()
            resp = await client.get("/api/status")
            resp.raise_for_status()
            data = resp.json()
            data["latency_ms"] = round((time.monotonic() - t0) * 1000, 1)
            return data
        except httpx.HTTPError as exc:
            logger.warning("RaidAPI status request failed: %s", exc)
            return None

    async def request_telemetry(self) -> tuple[dict[str, Any] | None, str | None]:
        res = await self.send_command("telemetry")
        if res is None:
            return None, "can't reach Para-RAID server"
        if res.get("status") != "ok":
            return res, res.get("detail") or "telemetry error"
        return res, None

    async def capture_photo(self, timeout: float = 2.5) -> tuple[bytes | None, str | None]:
        client = self._get_client()
        try:
            resp = await client.get(
                "/api/photo",
                params={"fresh": "true", "timeout": timeout},
                timeout=timeout + 2.0,
            )
            if resp.status_code == 200 and resp.content:
                return resp.content, None
            try:
                detail = resp.json().get("detail", "")
            except:
                detail = f"HTTP {resp.status_code}"
            return None, detail or f"HTTP {resp.status_code}"
        except httpx.HTTPError as exc:
            logger.warning("RaidAPI photo request failed: %s", exc)
            return None, str(exc)


raid_api = RaidAPIClient()
