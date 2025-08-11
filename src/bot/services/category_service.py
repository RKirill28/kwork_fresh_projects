# Сохрраняем категори
from aiogram.fsm.context import FSMContext

from parser.kwork_api_service import CategoryData

from bot.states import Menu

from parser.categories_parser_service import TelegramCategory


class CategoryServiceException(Exception):
    """Ошибка в работе сервиса категорий"""


async def build_category_data(state: FSMContext, id: int) -> CategoryData:
    """Получает CategoryData из полученного id и состояни"""
    curr_state = await state.get_state()

    if curr_state == Menu.choose_main_cat.state:
        return CategoryData(id, None, None)
    elif curr_state == Menu.choose_sub_cat.state:
        return CategoryData(None, id, None)
    elif curr_state == Menu.choose_attr.state:
        sub_cat_id = await state.get_value('sub_cat_id')
        if sub_cat_id is None: 
            raise CategoryServiceException('Нету sub_cat_id')

        return CategoryData(None, sub_cat_id, id) 
    else:
        raise CategoryServiceException('Не удалось собрать CategoryData из полученного id!')

def set_selected_cats(categories: list[TelegramCategory], category_ids: set[int]) -> list[TelegramCategory]:
    for cat in categories:
        if cat.id in category_ids:
            cat.selected = True
        for sub_cat in cat.sub_categories:
            if sub_cat.id in category_ids:
                sub_cat.selected = True
            for attr in sub_cat.attrs:
                if attr.id in category_ids:
                    attr.selected = True
    return categories

