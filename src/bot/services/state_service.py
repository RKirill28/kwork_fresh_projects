# Work with FSMContext

from typing import Literal

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from parser.kwork_api_service import CategoryData

from bot.exception import TelegramBotException, StateWorkException
from bot.states import Menu


async def init_menu_state(state: FSMContext) -> None:
    """Загружает текущее состояние парсера и устанавливает состояние на меню"""
    parser_state = await state.get_value('parser_state')
    if parser_state is None:
        await state.update_data(parser_state=False) 
    await state.set_state(Menu.menu)

async def get_parser_state(state: FSMContext) -> bool:
    """Получает состояние парсера"""
    parser_state: bool|None = await state.get_value('parser_state')
    if parser_state is None: raise StateWorkException('Нету parser_state ключа')
    return parser_state
