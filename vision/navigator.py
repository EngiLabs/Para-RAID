from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Waypoint:
    x: float
    y: float


class Navigator:
    def __init__(self) -> None:
        self._path: list[Waypoint] = []
        self._obstacle_map: np.ndarray = np.zeros((100, 100), dtype=np.uint8)

    async def plan_path(self, start_x: float, start_y: float, goal_x: float, goal_y: float) -> list[Waypoint]:
        self._path = [
            Waypoint(x=start_x, y=start_y),
            Waypoint(x=goal_x,  y=goal_y),
        ]
        logger.info(
            "Path planned: (%.2f, %.2f) -> (%.2f, %.2f), %d waypoints",
            start_x, start_y, goal_x, goal_y, len(self._path),
        )
        return self._path

    async def update_obstacles(self, obstacle_data: np.ndarray) -> None:
        self._obstacle_map = obstacle_data
        logger.debug("Obstacle map updated, shape=%s", obstacle_data.shape)

    @staticmethod
    def distance(p1: Waypoint, p2: Waypoint) -> float:
        return math.hypot(p2.x - p1.x, p2.y - p1.y)

    @property
    def current_path(self) -> list[Waypoint]:
        return list(self._path)
