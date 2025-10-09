from typing import Iterable

# from services.saver_service import init_json_file, save_new_projects_to_json
from services.parser_service import ProjectData, parse
from services.kwork_api_service import ApiResponse, get_project_by_page, CategoryData

from business.project_filter import get_new_projects

import asyncio


async def get_first_project(
    categories: Iterable[CategoryData], user_id: int
) -> ProjectData:
    """Парсит первый проектс"""
    tasks = []
    for cateogry in categories:
        tasks.append(get_project_by_page(category=cateogry))

    projects_from_api: list[ApiResponse] = await asyncio.gather(*tasks)
    parsed_projects: list[ProjectData] = parse(projects_from_api)
    parsed_projects = sorted(parsed_projects, key=lambda obj: obj.date_active)
    return parsed_projects[-1]


async def parse_kwork(
    categories: Iterable[CategoryData], user_id: int
) -> list[ProjectData]:
    """Парсит кворк и возвращает новые данные"""
    tasks = []
    for cateogry in categories:
        tasks.append(get_project_by_page(category=cateogry))

    projects_from_api: list[ApiResponse] = await asyncio.gather(*tasks)
    parsed_projects: list[ProjectData] = parse(projects_from_api)

    new_projects = get_new_projects(parsed_data=parsed_projects, user_id=user_id)

    return new_projects
