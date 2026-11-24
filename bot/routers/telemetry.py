from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from ..api_client import raid_api

router = Router(name="spidor_telemetry")


async def _reply_status(message_link: Message) -> None:
    data = await raid_api.get_status()
    if not data:
        await message_link.answer("server is unreachable")
        return
    latency = data.get("latency_ms")
    lat_str = f" ({latency} ms)" if latency is not None else ""
    body = data.get("formatted_status") or data.get("formatted") or str(data)
    await message_link.answer(f"server is online{lat_str}\n{body}")


async def _reply_telemetry(message_link: Message) -> None:
    data, err = await raid_api.request_telemetry()
    if data is None:
        await message_link.answer("server is unreachable")
        return
    if err:
        await message_link.answer(f"telemetry gathering error: {err}")
        return
    body = data.get("formatted") or str(data.get("snapshot", {}).get("telemetry", data))
    await message_link.answer(f"telemetry:\n\n{body}")


@router.message(Command("status"))
async def cmd_status(message: Message):
    await _reply_status(message)


@router.callback_query(F.data == "req_status")
async def cb_status(callback: CallbackQuery):
    await _reply_status(callback.message)
    await callback.answer()


@router.message(Command("telemetry"))
async def cmd_telemetry(message: Message):
    await _reply_telemetry(message)


@router.callback_query(F.data == "req_telemetry")
async def cb_telemetry(callback: CallbackQuery):
    await _reply_telemetry(callback.message)
    await callback.answer()
