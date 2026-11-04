from __future__ import annotations

import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from core.raid import raid
from core.state import state_snapshot
from server.network.ws_handler import handle_ws_message

logger = logging.getLogger(__name__)

app = FastAPI(title="Para-RAID", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    raid.bind(ws)
    await state_snapshot.set_connected(True)
    logger.info("unit connected via WS")

    try:
        while True:
            raw = await ws.receive_text()
            response = await handle_ws_message(raw)
            if response:
                await ws.send_text(json.dumps(response))
    except WebSocketDisconnect:
        logger.info("unit disconnected")
    finally:
        raid.unbind()
        await state_snapshot.set_connected(False)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "connected": str(state_snapshot.connected)}
