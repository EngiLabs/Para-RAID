from __future__ import annotations

import asyncio
import logging

import cv2
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaRelay

from core.state import state_snapshot
from vision.pipeline import VisionPipeline

logger = logging.getLogger(__name__)


class WebRTCHandler:
    def __init__(self) -> None:
        self._pc: RTCPeerConnection | None = None
        self._relay = MediaRelay()
        self._pipeline = VisionPipeline()
        self._consume_task: asyncio.Task | None = None

    async def handle_offer(self, sdp: str, sdp_type: str) -> RTCSessionDescription:
        if self._pc:
            await self.close()

        self._pc = RTCPeerConnection()

        @self._pc.on("track")
        async def on_track(track: MediaStreamTrack):
            if track.kind == "video":
                logger.info("video track received from robot")
                subscribed_track = self._relay.subscribe(track)
                self._consume_task = asyncio.create_task(self._consume_video(subscribed_track))

        @self._pc.on("connectionstatechange")
        async def on_state_change():
            state = self._pc.connectionState
            logger.info("WebRTC connection state: %s", state)
            if state in ("failed", "closed"):
                await self.close()

        offer = RTCSessionDescription(sdp=sdp, type=sdp_type)
        await self._pc.setRemoteDescription(offer)
        answer = await self._pc.createAnswer()
        await self._pc.setLocalDescription(answer)
        return self._pc.localDescription

    async def _consume_video(self, track: MediaStreamTrack) -> None:
        try:
            while True:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
                await self._pipeline.process_frame(img)
                _, buffer = cv2.imencode(".jpg", img)
                await state_snapshot.store_frame(buffer.tobytes())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.info("video stream reading stopped: %s", e)

    async def add_ice_candidate(self, candidate: dict) -> None:
        if not self._pc or not candidate:
            return
        logger.debug("adding ICE candidate: %s", candidate)

    async def close(self) -> None:
        if self._consume_task and not self._consume_task.done():
            self._consume_task.cancel()
            try:
                await self._consume_task
            except asyncio.CancelledError:
                pass
            self._consume_task = None

        if self._pc:
            await self._pc.close()
            self._pc = None


webrtc_handler = WebRTCHandler()
