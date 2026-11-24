from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Telemetry:
    imu_roll: float = .0
    imu_pitch: float = .0
    imu_yaw: float = .0
    ir_sensors: list[float] = field(default_factory=list)


@dataclass
class Position:
    x: float = .0
    y: float = .0
    heading: float = .0


@dataclass
class Snapshot:
    connected: bool = False
    telemetry: Telemetry = field(default_factory=Telemetry)
    position: Position = field(default_factory=Position)
    current_gait: str = "walk"
    map_points: list[dict[str, Any]] = field(default_factory=list)
    saved_points: dict[str, Position] = field(default_factory=dict)
    last_frame: bytes | None = None
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def update_telemetry(self, data: dict[str, Any]) -> None:
        async with self._lock:
            self.telemetry = Telemetry(
                imu_roll=data.get("imu_roll", self.telemetry.imu_roll),
                imu_pitch=data.get("imu_pitch", self.telemetry.imu_pitch),
                imu_yaw=data.get("imu_yaw", self.telemetry.imu_yaw),
                ir_sensors=data.get("ir_sensors", self.telemetry.ir_sensors),
            )

    async def update_position(self, x: float, y: float, heading: float) -> None:
        async with self._lock:
            self.position = Position(x=x, y=y, heading=heading)

    async def set_connected(self, status: bool) -> None:
        async with self._lock:
            self.connected = status

    async def store_frame(self, frame_bytes: bytes) -> None:
        async with self._lock:
            self.last_frame = frame_bytes

    async def get_snapshot(self) -> bytes | None:
        async with self._lock:
            return self.last_frame

    def to_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "telemetry": {
                "imu_roll": self.telemetry.imu_roll,
                "imu_pitch": self.telemetry.imu_pitch,
                "imu_yaw": self.telemetry.imu_yaw,
                "ir_sensors": self.telemetry.ir_sensors,
            },
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "heading": self.position.heading,
            },
            "current_gait": self.current_gait,
            "has_frame": self.last_frame is not None,
        }

    def format_status(self) -> str:
        t = self.telemetry
        return (f"""
connection: {'✅' if self.connected else '❌'}
IR: {t.ir_sensors}
IMU: R={t.imu_roll:.1f} P={t.imu_pitch:.1f} Y={t.imu_yaw:.1f}
gait: {self.current_gait}
position: ({self.position.x:.2f}, {self.position.y:.2f}) H={self.position.heading:.1f}°
"""[1:-1]
        )


state_snapshot = Snapshot()
