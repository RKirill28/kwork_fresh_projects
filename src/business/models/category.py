from dataclasses import dataclass
from typing import NamedTuple
from pydantic import BaseModel, Field


@dataclass(frozen=True)
class CategoryData:
    main_id: int | None
    sub_id: int | None 
    attr_id: int | None

class ApiResponse(NamedTuple):
    json: dict
    category: CategoryData

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
