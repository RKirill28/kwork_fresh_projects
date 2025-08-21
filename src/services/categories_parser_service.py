import json

from pathlib import Path
from pydantic import ValidationError

from business.models.category import TelegramAttr, TelegramCategory, TelegramSubCategory


class CategoryParserException(Exception):
    """Ошибка в работе парсера категорий"""


def parse(path: Path) -> list[TelegramCategory]:
    with open(path.resolve(), "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        return [TelegramCategory.model_validate(category) for category in data]
    except ValidationError as e:
        raise CategoryParserException(f"Ошибка валидации: {e.json()}")


# def get_sub_cats(categories: list[TelegramCategory], cat_id: int) -> list[TelegramSubCategory] | list[TelegramAttr]:
# def get_categories(cats: list[Category] | list[SubCategory] | list[Attr]) -> list[TelegramCategory]:
#     return [
#         TelegramCategory(
#             selected=False,
#         )
#         for cat in cats
#     ]


def get_sub_cats(
    categories: list[TelegramCategory], cat_id: int
) -> list[TelegramSubCategory] | list[TelegramAttr]:
    """Получает только список подкатегорий для main_cat или sub_cat"""
    for cat in categories:
        if cat.id == cat_id:
            return cat.sub_categories

    for cat in categories:
        for sub_cat in cat.sub_categories:
            if sub_cat.id == cat_id:
                return sub_cat.attrs
    raise CategoryParserException(
        f"Не удалось получить подкатегори главной категории id: {cat_id}"
    )
