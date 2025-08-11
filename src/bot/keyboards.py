from aiogram.filters import callback_data
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from parser.categories_parser_service import Attr, Category, SubCategory, TelegramCategory, TelegramSubCategory, TelegramAttr
from parser.kwork_api_service import CategoryData


class ToCatData(CallbackData, prefix='to_cat'):
    main_cat_id: int | None = None
    sub_cat_id: int | None = None
    per_cat_id: int | None = None

class SelectCategory(CallbackData, prefix='select'):
    main_id: int | None = None
    sub_id: int | None = None
    attr_id: int | None = None

class ChooseCategoryData(CallbackData, prefix='choose_category'):
    main_cat_id: int | None
    sub_cat_id: int | None
    attr_id: int | None


def show_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='📌 Главное меню')],
            [KeyboardButton(text='👤 Об авторе бота')]
        ],
        resize_keyboard=True
    )

def show_parser_menu(parser_state: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⚙️ Настройки парсера', callback_data='settings')],
            [InlineKeyboardButton(text='⏸️ Стоп' if parser_state else '▶️ Старт', callback_data='parser_toggle')],
        ]
    )

def show_settings_parser_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🗂 Выбрать категории', callback_data='choice_category')],
            [InlineKeyboardButton(text='⏳ Установить частоту проверки биржи', callback_data='set_time_parse')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')]
        ]
    )

def get_category_menu(cats: list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for cat in cats:
        if isinstance(cat, (TelegramCategory, TelegramSubCategory)):
            builder.row(
                InlineKeyboardButton(
                    text=f' + {cat.name}' if cat.selected else cat.name,
                    callback_data=f'select:{cat.id}'
                ),
                InlineKeyboardButton(text='➡️', callback_data=str(cat.id))
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text=f' + {cat.name}' if cat.selected else cat.name,
                    callback_data=f'select:{cat.id}'
                ),
            )    

    builder.row(
        InlineKeyboardButton(text='✅ Сохранить и в гл. меню', callback_data='save')
    )
    builder.row(
        InlineKeyboardButton(text='⬅️ Назад', callback_data='back_cat'),
    )

    return builder.as_markup()

