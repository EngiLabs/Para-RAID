from fastapi import APIRouter, HTTPException, Query, Response
from core import raid, state_snapshot


router = APIRouter()


@router.get("/photo")
async def get_photo(
    fresh: bool = Query(default=False),
    timeout: float = Query(default=2.5, ge=0.1, le=10.0),
) -> Response:
    if fresh:
        if not raid.is_connected:
            raise HTTPException(status_code=503, detail="robot not connected")
        seq = state_snapshot.frame_seq
        ok = await raid.capture_photo()
        if not ok:
            raise HTTPException(status_code=502, detail="failed to send photo request to unit")
        frame = await state_snapshot.wait_next_frame(seq, timeout=timeout)
        if frame is None:
            raise HTTPException(status_code=504, detail="timed out waiting for frame from unit")
        return Response(content=frame, media_type="image/jpeg")

    frame = await state_snapshot.get_snapshot()
    if frame is None:
        await raid.capture_photo()
        raise HTTPException(status_code=404, detail="no frame in cache yet, capture request sent to unit")
    return Response(content=frame, media_type="image/jpeg")
