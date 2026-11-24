from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Telemetry:
    imu_accel: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    imu_gyro: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
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
    _last_imu_ts: float | None = field(default=None, repr=False)
    _imu_initialized: bool = field(default=False, repr=False)
    _last_telemetry_ts: float | None = field(default=None, repr=False)
    _telemetry_seq: int = field(default=0, repr=False)
    _telemetry_cond: asyncio.Condition = field(default_factory=asyncio.Condition, repr=False)
    _frame_seq: int = field(default=0, repr=False)
    _frame_cond: asyncio.Condition = field(default_factory=asyncio.Condition, repr=False)

    @property
    def telemetry_seq(self) -> int:
        return self._telemetry_seq

    def telemetry_age_s(self) -> float | None:
        if self._last_telemetry_ts is None:
            return None
        return round(max(0.0, time.monotonic() - self._last_telemetry_ts), 2)

    async def update_telemetry(self, data: dict[str, Any]) -> None:
        async with self._lock:
            imu = data.get("imu") if isinstance(data.get("imu"), dict) else {}
            accel = self._vec3(imu.get("accel", data.get("imu_accel", self.telemetry.imu_accel)))
            gyro = self._vec3(imu.get("gyro", data.get("imu_gyro", self.telemetry.imu_gyro)))

            now = time.monotonic()
            dt = 0.0 if self._last_imu_ts is None else min(max(now - self._last_imu_ts, 0.0), 1.0)
            self._last_imu_ts = now
            self._last_telemetry_ts = now
            self._telemetry_seq += 1

            roll, pitch, yaw = self._estimate_orientation(accel, gyro, dt)
            roll = float(data.get("imu_roll", roll))
            pitch = float(data.get("imu_pitch", pitch))
            yaw = float(data.get("imu_yaw", yaw))

            self.telemetry = Telemetry(
                imu_accel=accel,
                imu_gyro=gyro,
                imu_roll=roll,
                imu_pitch=pitch,
                imu_yaw=yaw,
                ir_sensors=data.get("ir_sensors", self.telemetry.ir_sensors),
            )
        async with self._telemetry_cond:
            self._telemetry_cond.notify_all()

    async def wait_next_telemetry(self, after_seq: int, timeout: float = 1.0) -> bool:
        async def _wait() -> None:
            async with self._telemetry_cond:
                await self._telemetry_cond.wait_for(lambda: self._telemetry_seq > after_seq)

        try:
            await asyncio.wait_for(_wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False

    @staticmethod
    def _vec3(values: Any) -> list[float]:
        if isinstance(values, (list, tuple)) and len(values) >= 3:
            return [float(values[0]), float(values[1]), float(values[2])]
        return [0.0, 0.0, 0.0]

    def _estimate_orientation(self, accel: list[float], gyro: list[float], dt: float) -> tuple[float, float, float]:
        ax, ay, az = accel
        gx, gy, gz = gyro

        roll = self.telemetry.imu_roll + math.degrees(gx) * dt
        pitch = self.telemetry.imu_pitch + math.degrees(gy) * dt
        yaw = ((self.telemetry.imu_yaw + math.degrees(gz) * dt + 180.0) % 360.0) - 180.0

        accel_norm = math.sqrt(ax * ax + ay * ay + az * az)
        if accel_norm > 1e-3:
            roll_acc = math.degrees(math.atan2(ay, math.hypot(ax, az)))
            pitch_acc = math.degrees(math.atan2(-ax, math.hypot(ay, az)))
            if not self._imu_initialized:
                roll, pitch = roll_acc, pitch_acc
                self._imu_initialized = True
            else:
                alpha = 0.98
                roll = alpha * roll + (1.0 - alpha) * roll_acc
                pitch = alpha * pitch + (1.0 - alpha) * pitch_acc

        return round(roll, 2), round(pitch, 2), round(yaw, 2)

    async def update_position(self, x: float, y: float, heading: float) -> None:
        async with self._lock:
            self.position = Position(x=x, y=y, heading=heading)

    async def set_connected(self, status: bool) -> None:
        async with self._lock:
            self.connected = status

    @property
    def frame_seq(self) -> int:
        return self._frame_seq

    async def store_frame(self, frame_bytes: bytes) -> None:
        async with self._lock:
            self.last_frame = frame_bytes
            self._frame_seq += 1
        async with self._frame_cond:
            self._frame_cond.notify_all()

    async def get_snapshot(self) -> bytes | None:
        async with self._lock:
            return self.last_frame

    async def wait_next_frame(self, after_seq: int, timeout: float = 2.0) -> bytes | None:
        async def _wait() -> None:
            async with self._frame_cond:
                await self._frame_cond.wait_for(lambda: self._frame_seq > after_seq)

        try:
            await asyncio.wait_for(_wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
        return await self.get_snapshot()

    def to_dict(self) -> dict[str, Any]:
        age_s = self.telemetry_age_s()
        return {
            "connected": self.connected,
            "telemetry_received": age_s is not None,
            "telemetry_age_s": age_s,
            "telemetry": {
                "imu_accel": list(self.telemetry.imu_accel),
                "imu_gyro": list(self.telemetry.imu_gyro),
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

    def format_server_status(self) -> str:
        age_s = self.telemetry_age_s()
        telem_state = f"{age_s:.1f}s ago" if age_s is not None else "no data yet"
        return (
            f"unit WS: {'connected' if self.connected else 'disconnected'}\n"
            f"gait: {self.current_gait}\n"
            f"telemetry stream: {telem_state}\n"
            f"camera cache: {'yeah' if self.last_frame is not None else 'nope'}"
        )

    def format_telemetry(self) -> str:
        t = self.telemetry
        age_s = self.telemetry_age_s()
        freshness = f"{age_s:.1f}s ago" if age_s is not None else "never received"
        return (
            f"freshness: {freshness}\n"
            f"IR: {t.ir_sensors}\n"
            f"IMU: R={t.imu_roll:.1f}° P={t.imu_pitch:.1f}° Y={t.imu_yaw:.1f}°\n"
            f"IMU acceleration: {t.imu_accel} | gyro: {t.imu_gyro}\n"
            f"position: ({self.position.x:.2f}, {self.position.y:.2f}) H={self.position.heading:.1f}°"
        )

    def format_status(self) -> str:
        return f"{self.format_server_status()}\n{self.format_telemetry()}"


state_snapshot = Snapshot()
