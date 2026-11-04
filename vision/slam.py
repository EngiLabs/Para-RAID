from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MapPoint:
    x: float
    y: float
    z: float
    descriptor: np.ndarray | None = None


class MonocularSLAM:
    def __init__(self) -> None:
        self._map_points: list[MapPoint] = []
        self._keyframes: list[np.ndarray] = []
        self._current_pose: np.ndarray = np.eye(4)

    async def process_frame(self, frame: np.ndarray) -> np.ndarray:
        gray = frame if len(frame.shape) == 2 else np.mean(frame, axis=2).astype(np.uint8)
        self._keyframes.append(gray)
        if len(self._keyframes) > 100:
            self._keyframes.pop(0)
        logger.debug("SLAM keyframes: %d, map points: %d", len(self._keyframes), len(self._map_points))
        return self._current_pose

    @property
    def pose(self) -> np.ndarray:
        return self._current_pose.copy()

    @property
    def map_points(self) -> list[MapPoint]:
        return list(self._map_points)

    def get_map_as_dict(self) -> list[dict[str, float]]:
        return [{"x": p.x, "y": p.y, "z": p.z} for p in self._map_points]
