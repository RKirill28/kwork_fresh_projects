from dataclasses import dataclass
import json

from pathlib import Path
from pydantic import BaseModel, Field, ValidationError


class CategoryParserException(Exception):
    """Ошибка в работе парсера категорий"""

class Attr(BaseModel):
    id: int
    name: str = Field(alias='title')

class SubCategory(BaseModel):
    id: int 
    name: str
    attrs: list['TelegramAttr'] = []

class Category(BaseModel):
    id: int 
    name: str
    sub_categories: list['TelegramSubCategory'] 

class Categories(BaseModel):
    categories: list[Category]

class TelegramAttr(Attr):
    selected: bool = False

class TelegramSubCategory(SubCategory):
    selected: bool = False

class TelegramCategory(Category):
    selected: bool = False


def parse(path: Path) -> list[TelegramCategory]:
    with open(path.resolve(), 'r', encoding='utf-8') as f:
        data = json.load(f)
    try:
        return [TelegramCategory.model_validate(category) for category in data]
    except ValidationError as e: 
        raise CategoryParserException(f'Ошибка валидации: {e.json()}')

# def get_categories(cats: list[Category] | list[SubCategory] | list[Attr]) -> list[TelegramCategory]:
#     return [
#         TelegramCategory(
#             selected=False, 
#         )
#         for cat in cats
#     ]

def get_sub_cats(categories: list[Category], cat_id: int) -> list[SubCategory] | list[Attr]:
    """Получает только список подкатегорий для main_cat или sub_cat"""
    for cat in categories:
        if cat.id == cat_id:
            return cat.sub_categories
    
    for cat in categories:
        for sub_cat in cat.sub_categories:
            if sub_cat.id == cat_id:
                return sub_cat.attrs
    raise CategoryParserException(f'Не удалось получить подкатегори главной категории id: {cat_id}')
