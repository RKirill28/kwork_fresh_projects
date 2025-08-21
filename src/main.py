import asyncio
import datetime
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from config import settings

from bot.handlers import router

from services.storage_service import init_json_file


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(
        token=settings.bot_config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger_format = "%(levelname)s:%(name)s:%(funcName)s() - %(message)s"
    logging.basicConfig(level=logging.INFO, format=logger_format)

    logger = logging.getLogger()
    foramtter = logging.Formatter(logger_format)

    file_handler = logging.FileHandler(
        f"./logs/{datetime.datetime.now().strftime('%Y:%m:%d - %H:%M:%S')}_bot.log",
        encoding="utf-8",
        mode="a",
    )
    file_handler.setFormatter(foramtter)
    file_handler.setLevel(logging.DEBUG)

    init_json_file(settings.file_config.user_data)

    # logger.addHandler(file_handler) - # WARN add after deploy

    asyncio.run(main())
