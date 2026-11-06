import logging
import uvicorn
from asyncio import run, gather
from sys import argv

import config as global_config

from bot import create_bot, create_dispatcher, update_bot_stats
from server import app
from server.network.webrtc_handler import webrtc_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
logging.getLogger("aiogram.dispatcher").disabled = True


async def run_bot(cmd: list[str]) -> None:
    logger.info("starting Telegram bot...")
    bot = create_bot()
    await bot.delete_webhook(drop_pending_updates=True)
    dp = create_dispatcher()
    try:
        if len(cmd) > 0 and cmd[0] == "update":
            await update_bot_stats(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def run_server() -> None:
    logger.info(
        "starting WebRTC & CUDA router...",
        global_config.SERVER_HOST,
        global_config.SERVER_PORT
    )
    webrtc_handler.pipeline.load_model()
    await webrtc_handler.pipeline.start()

    config = uvicorn.Config(
        app,
        host=global_config.SERVER_HOST,
        port=global_config.SERVER_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    logger.info(
        "starting FastAPI server on %s:%d...",
        global_config.SERVER_HOST,
        global_config.SERVER_PORT
    )
    await server.serve()


async def startup(to_launch: list[str]) -> None:
    logger.info(r"""
 ____                       ____      _    ___ ____  
|  _ \ __ _ _ __ __ _      |  _ \    / \  |_ _|  _ \ 
| |_) / _` | '__/ _` |_____| |_) |  / _ \  | || | | |
|  __/ (_| | | | (_| |_____|  _ <  / ___ \ | || |_| |
|_|   \__,_|_|  \__,_|     |_| \_\/_/   \_\___|____/ 
""")
    if len(to_launch) > 0 and to_launch[0] == "bot":
        await run_bot(to_launch[1:] if len(to_launch) > 1 else [])
    elif len(to_launch) > 0 and to_launch[0] == "server":
        await run_server()
    else:
        await gather(
            run_server(),
            run_bot([]),
        )


if __name__ == "__main__":
    run(startup(argv[1:] if len(argv) > 1 else []))
