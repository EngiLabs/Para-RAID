import asyncio
import logging
import numpy as np

from vision import slam

logger = logging.getLogger(__name__)


class VisionPipeline:
    def __init__(self) -> None:
        self._model = None
        self._queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=1)
        self._worker_task: asyncio.Task | None = None

    def load_model(self, device: str = "cuda") -> None:
        logger.info("loading Depth Anything V2 onto %s...", device)
        # загрузка и warmup нулевым тензором должна быть здесь
        logger.info("model loaded and ready")

    async def start(self) -> None:
        self._worker_task = asyncio.create_task(self._inference_loop())

    async def process_frame(self, frame: np.ndarray) -> None:
        if self._queue.full():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        await self._queue.put(frame)

    async def _inference_loop(self) -> None:
        while True:
            frame = await self._queue.get()
            depth_map = await asyncio.to_thread(self._run_inference, frame)

            await slam.update(depth_map)

    def _run_inference(self, frame: np.ndarray) -> np.ndarray:
        # return self._model.infer(frame)
        return frame
