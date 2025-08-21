from aiogram.fsm.context import FSMContext

from bot.exception import StateWorkException
from bot.states import Menu

from business.models.category import TelegramSubCategory


async def init_menu_state(state: FSMContext) -> None:
    """Загружает текущее состояние парсера и устанавливает состояние на меню"""
    parser_state = await state.get_value("parser_state")
    if parser_state is None:
        await state.update_data(parser_state=False)
    await state.set_state(Menu.menu)


async def get_parser_state(state: FSMContext) -> bool:
    """Получает состояние парсера"""
    parser_state: bool | None = await state.get_value("parser_state")
    if parser_state is None:
        raise StateWorkException("Нету parser_state ключа")
    return parser_state


async def get_key_by_state(state: FSMContext):
    """Получаю ключ в зависимости от состояния"""
    curr_state = await state.get_state()
    if curr_state == Menu.choose_main_cat.state:
        return "main_cats"
    elif curr_state == Menu.choose_sub_cat.state:
        return "sub_cats"
    elif curr_state == Menu.choose_attr.state:
        return "attrs"
    else:
        raise StateWorkException("Не удалось получить ключ, неизвестное состояние")


async def get_sub_cats(state: FSMContext) -> list[TelegramSubCategory]:
    sub_cats: list[TelegramSubCategory] | None = await state.get_value("sub_cats")
    if sub_cats is None:
        return []
    return sub_cats
