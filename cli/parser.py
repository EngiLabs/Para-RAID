from __future__ import annotations

import re
from typing import Any


def parse_distance_or_duration(token: str) -> tuple[float | None, float | None]:
    token = token.strip().lower()
    if not token:
        return None, None

    m_ms = re.fullmatch(r"(\d+(?:\.\d+)?)\s*ms", token)
    if m_ms:
        return None, float(m_ms.group(1)) / 1000.

    m_s = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:s|sec)", token)
    if m_s:
        return None, float(m_s.group(1))

    m_cm = re.fullmatch(r"(\d+(?:\.\d+)?)\s*cm", token)
    if m_cm:
        return float(m_cm.group(1)) / 100., None

    m_mm = re.fullmatch(r"(\d+(?:\.\d+)?)\s*mm", token)
    if m_mm:
        return float(m_mm.group(1)) / 1000., None

    m_m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*m?", token)
    if m_m:
        return float(m_m.group(1)), None

    raise ValueError(f"unknown format: '{token}'\nskill issue, i guess")


def parse_command(raw_input: str, current_speed: int = 255) -> dict[str, Any] | None:
    raw = raw_input.strip()
    if not raw:
        return None

    tokens = raw.split()
    cmd = tokens[0].lower()
    args = tokens[1:]

    direction_aliases = {
        "forward": "forward", "fwd": "forward", "w": "forward",
        "backward": "backward", "back": "backward", "bwd": "backward", "s": "backward",
        "left": "left", "l": "left", "a": "left",
        "right": "right", "r": "right", "d": "right",
    }

    if cmd in direction_aliases:
        direction = direction_aliases[cmd]
        dist_m = None
        dur_s = None
        speed = current_speed

        if len(args) >= 1:
            dist_m, dur_s = parse_distance_or_duration(args[0])
        if len(args) >= 2:
            try:
                speed = max(1, min(255, int(args[1])))
            except ValueError:
                pass

        return {
            "action": direction,
            "direction": direction,
            "distance_m": dist_m,
            "duration_s": dur_s,
            "speed": speed,
        }

    if cmd in ("stop", "halt", "x"):
        return {"action": "stop"}

    if cmd in ("speed", "set_speed"):
        if not args:
            raise ValueError("should set value (1-255)")
        return {"action": "local_speed", "speed": max(1, min(255, int(args[0])))}

    if cmd in ("gait", "set_gait"):
        if not args:
            raise ValueError("only 'walk', 'trot' or 'creep'")
        gait_name = args[0].lower()
        if gait_name not in ("walk", "trot", "creep"):
            raise ValueError(f"unknown format: '{gait_name}'\nskill issue, i guess")
        return {"action": "set_gait", "gait": gait_name}

    if cmd == "home":
        return {"action": "home"}

    if cmd == "relax":
        return {"action": "relax"}

    if cmd == "wake":
        return {"action": "wake"}

    if cmd in ("pose", "set_pose"):
        if len(args) < 3:
            raise ValueError("wtf ya doing bro")
        return {"action": "set_pose", "roll": int(args[0]), "pitch": int(args[1]), "yaw": int(args[2])}

    if cmd in ("led", "set_led"):
        if not args:
            raise ValueError("wtf ya doing bro")
        return {"action": "set_led", "state": 1 if args[0].lower() in ("on", "1", "true") else 0}

    if cmd in ("photo", "shot", "capture"):
        return {"action": "photo", "save_path": args[0] if args else None}

    if cmd in ("goto", "navigate", "nav"):
        if len(args) < 2:
            raise ValueError("wtf ya doing bro")
        return {"action": "goto", "x": float(args[0]), "y": float(args[1])}

    if cmd in ("status", "telemetry", "stat"):
        return {"action": "status"}

    if cmd in ("help", "?"):
        return {"action": "help"}

    if cmd in ("exit", "quit", "q"):
        return {"action": "exit"}

    raise ValueError(f"unknown cmd: '{cmd}'\nskill issue, i guess")  # он сам это написал
