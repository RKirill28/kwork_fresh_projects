<<<<<<< Updated upstream
=======
# import asyncio
# import json
# import os
#
# from pathlib import Path
#
# from parser.kwork_api_service import Category
# from parser import init_projects_to_json, parse_kwork, parse_missed_projects
# from parser.saver_service import _serialize_datetime_to_iso
#
# from bot.services.parser_categories_service import parse
#
# from config import settings
#
# from dataclasses import asdict
#
#
# async def init_json(file_path: Path, categories: list[Category]):
#     if not os.path.exists(file_path.resolve()):
#         print('Инитю')
#         with open(file_path.resolve(), 'w') as f: f.write('{}')
#         await init_projects_to_json(file_path=file_path, categories=categories)
#     else:
#         with open(file_path.resolve(), 'r') as f:
#             if not f.read():
#                 print('Инитю')
#                 with open(file_path.resolve(), 'w') as _f: _f.write('{}')
#                 await init_projects_to_json(file_path=file_path, categories=categories)
#
# async def main():
#     file = settings.file_config.projects_path
#     categories = [Category(main_id=38), Category(sub_id=41, attr_id=211), Category(sub_id=41, attr_id=3587), Category(sub_id=41, attr_id=7352)]
#
#     await init_json(file, categories)
#
#     missed_data = await parse_missed_projects(file, categories)
#
#     missed_data = {project.id: asdict(project) for project in missed_data}
#     with open('./missed.json', 'w', encoding='utf-8') as f:
#         json.dump(missed_data, f, default=_serialize_datetime_to_iso, indent=4, ensure_ascii=False)
#
#     while True:
#         print('Ждем...')
#         new_data = await parse_kwork(file, categories)
#         if new_data:
#             print(f'Опа {new_data[0].name}')
#             new_data = {project.id: asdict(project) for project in new_data}
#             with open('./new.json', 'w', encoding='utf-8') as f:
#                 json.dump(new_data, f, default=_serialize_datetime_to_iso, indent=4, ensure_ascii=False)
#         await asyncio.sleep(10)
#
# if __name__ == '__main__':
#    # asyncio.run(main())
#     res = parse(settings.file_config.cats_path)
#     print(res[0])
#

>>>>>>> Stashed changes
import asyncio
import datetime
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, Message, Update, TelegramObject
from aiogram.types.error_event import ErrorEvent
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

    init_json_file(settings.file_config.user_cats_path)
    init_json_file(settings.file_config.user_data)

    # logger.addHandler(file_handler) - # WARN add after deploy

    asyncio.run(main())
