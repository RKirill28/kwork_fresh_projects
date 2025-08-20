from aiogram.fsm.context import FSMContext

from bot.states import Menu

from business.models.category import TelegramCategory, TelegramSubCategory, TelegramAttr, CategoryData


TELEGRAM_CATEGORIES_TYPE = list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr]

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

def set_selected_cats(categories: list[TelegramCategory], user_cats: set[CategoryData]) -> list[TelegramCategory]:
    # просто поделил id на партии и потом проверял по ним
    main_ids = {cat.main_id for cat in user_cats if cat.main_id is not None}
    sub_ids = {cat.sub_id for cat in user_cats if cat.sub_id is not None and cat.attr_id is None}
    attr_pairs = {(cat.sub_id, cat.attr_id) for cat in user_cats if cat.sub_id is not None and cat.attr_id is not None}

    for category in categories:
        if category.id in main_ids:
            category.selected = True

        for sub in category.sub_categories:
            if sub.id in sub_ids:
                sub.selected = True

            for attr in sub.attrs:
                if (sub.id, attr.id) in attr_pairs:
                    attr.selected = True
    return categories

def change_selected(cats: TELEGRAM_CATEGORIES_TYPE, id: int) -> TELEGRAM_CATEGORIES_TYPE:
    for cat in cats:
        if cat.id == id:
            cat.selected = not cat.selected
    return cats

def build_selected_cats_text(categories: list[TelegramCategory]) -> str:
    selected_cats_text = ''
    for cat in categories:
        if cat.selected:
            selected_cats_text += f'· <u>{cat.name}</u>\n' 
        for sub_cat in cat.sub_categories:
            if sub_cat.selected:
                selected_cats_text += '· ' + cat.name + ' > ' + f'<u>{sub_cat.name}</u>\n' 
            for attr in sub_cat.attrs:
                if attr.selected:
                    selected_cats_text += '· ' + cat.name + ' > ' + sub_cat.name + ' > ' + f'<u>{attr.name}</u>\n'
    return selected_cats_text

# def category_data_to_text(category_data: CategoryData: list[TelegramCategory])
