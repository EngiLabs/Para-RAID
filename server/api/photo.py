from fastapi import APIRouter, HTTPException, Response
from core import raid, state_snapshot


router = APIRouter()


@router.get("/photo")
async def get_photo() -> Response:
    frame = await state_snapshot.get_snapshot()
    if frame is None:
        await raid.capture_photo()
        raise HTTPException(status_code=404, detail="no frame in cache yet, capture request sent to unit")
    return Response(content=frame, media_type="image/jpeg")
