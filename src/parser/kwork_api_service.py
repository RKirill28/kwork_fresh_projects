import aiohttp
import asyncio
import json

from typing import NamedTuple
from dataclasses import dataclass

from config import settings


class KworkApiError(Exception):
    """Ошибка при работе с API Kwork"""

@dataclass
class Category:
    main_id: int | None 
    sub_id: int | None 
    attr_id: int | None

class ApiResponse(NamedTuple):
    json: dict
    category: Category

async def _get_response(session: aiohttp.ClientSession, url: str) -> aiohttp.ClientResponse:
    async with session.post(url) as res:
        if res.status != 200: raise KworkApiError
        try:
            await res.read()
        except aiohttp.ClientResponseError: 
            raise KworkApiError
    return res

async def _get_json(response: aiohttp.ClientResponse) -> dict:
    try:
        return await response.json()
    except json.JSONDecodeError:
        raise KworkApiError

def _get_query_string_by_category(category: Category) -> str:
    if category.main_id is not None:
        return f'&c={category.main_id}'
    if category.attr_id is not None:
        return f'&c={category.sub_id}&attr={category.attr_id}'
    return f'&c={category.sub_id}'

async def get_project_by_page(category: Category, page: int = 1) -> ApiResponse:
    """Получает json c проектами на бирже указанной категории и страницы"""
    async with aiohttp.ClientSession() as session:
        response = await _get_response(session=session, url=settings.api_config.url+f'?page={page}'+_get_query_string_by_category(
            category=category
        ))
        json_res = await _get_json(response)
    return ApiResponse(json_res, category)

