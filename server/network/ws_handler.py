from __future__ import annotations

import json
import logging
from typing import Any

from core.state import state_snapshot
from server.network.webrtc_handler import WebRTCHandler

logger = logging.getLogger(__name__)

webrtc_handler = WebRTCHandler()


async def handle_ws_message(raw: str) -> dict[str, Any] | None:
    try:
        message = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("received invalid JSON: %s", raw[:200])
        return {"type": "error", "detail": "invalid JSON"}

    msg_type = message.get("type")

    if msg_type == "telemetry":
        await _handle_telemetry(message)
    elif msg_type == "status":
        await _handle_status(message)
    elif msg_type == "webrtc_offer":
        return await _handle_webrtc_offer(message)
    elif msg_type == "ice_candidate":
        await _handle_ice_candidate(message)
    else:
        logger.warning("unknown message type: %s", msg_type)

    return None


async def _handle_telemetry(message: dict[str, Any]) -> None:
    data = message.get("payload", {})
    await state_snapshot.update_telemetry(data)
    logger.debug("telemetry updated")


async def _handle_status(message: dict[str, Any]) -> None:
    payload = message.get("payload", {})
    if "gait" in payload:
        state_snapshot.current_gait = payload["gait"]
    logger.debug("status update: %s", payload)


async def _handle_webrtc_offer(message: dict[str, Any]) -> dict[str, Any]:
    sdp = message.get("sdp", "")
    sdp_type = message.get("sdp_type", "offer")
    answer = await webrtc_handler.handle_offer(sdp, sdp_type)
    return {
        "type": "webrtc_answer",
        "sdp": answer.sdp,
        "sdp_type": answer.type
    }


async def _handle_ice_candidate(message: dict[str, Any]) -> None:
    await webrtc_handler.add_ice_candidate(message.get("candidate", {}))
