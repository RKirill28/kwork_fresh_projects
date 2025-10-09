import aiohttp
import asyncio
import json

from business.models.category import ApiResponse, CategoryData
from business.category_rules import _get_query_string_by_category


class KworkApiError(Exception):
    """Ошибка при работе с API Kwork"""


class KworkApiBan(Exception):
    """Нет доступа к API Kwork"""


async def _get_response(
    session: aiohttp.ClientSession, url: str
) -> aiohttp.ClientResponse:
    async with session.post(url) as res:
        if res.status == 403:
            raise KworkApiBan

        if res.status != 200:
            raise KworkApiError(f"Код ответа: {res.status}")

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


async def get_project_by_page(category: CategoryData, page: int = 1) -> ApiResponse:
    """Получает json c проектами на бирже указанной категории и страницы"""
    async with aiohttp.ClientSession() as session:
        response = await _get_response(
            session=session,
            url=f"https://kwork.ru/projects?page={page}"
            + _get_query_string_by_category(category=category),
        )
        json_res = await _get_json(response)
    return ApiResponse(json_res, category)
