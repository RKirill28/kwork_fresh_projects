from pathlib import Path
from parser.saver_service import get_new_projects, save_new_projects_to_json
from parser.parser_service import Project, ProjectData, parse
from parser.kwork_api_service import ApiResponse, get_project_by_page, Category

import asyncio

async def init_projects_to_json(file_path: Path, categories: list[Category]) -> None:
    tasks = []
    for cateogry in categories:
        tasks.append(
            get_project_by_page(category=cateogry)
        )

    projects_from_api: list[ApiResponse] = await asyncio.gather(*tasks)
    parsed_projects = parse(projects_from_api) 

    save_new_projects_to_json(file_name=file_path, new_projects=parsed_projects)

async def parse_missed_projects(file_path: Path, categories: list[Category]) -> list[ProjectData]:
    """Получает пропущенные корвки"""
    page = 1
    
    missed_projects_for_tg = []
    while True:
        tasks = []
        for cateogry in categories:
            tasks.append(
                get_project_by_page(category=cateogry)
            )

        projects_from_api: list[ApiResponse] = await asyncio.gather(*tasks)
        parsed_projects_from_api = parse(projects_from_api) 

        new_projects = get_new_projects(
            file_name=file_path,
            parsed_data=parsed_projects_from_api
        )
        if len(new_projects) == 0: break
        missed_projects_for_tg.extend(new_projects)
        save_new_projects_to_json(file_name=file_path, new_projects=parsed_projects_from_api)

        page += 1
    return missed_projects_for_tg
    

async def parse_kwork(file_path: Path, categories: list[Category]) -> list[ProjectData]:
    """Парсит кворк и возвращает новые данные"""
    tasks = []
    for cateogry in categories:
        tasks.append(
            get_project_by_page(category=cateogry)
        )

    projects_from_api: list[ApiResponse] = await asyncio.gather(*tasks)
    parsed_projects_from_api: list[ProjectData] = parse(projects_from_api) 
        
    new_projects = get_new_projects(
        file_name=file_path,
        parsed_data=parsed_projects_from_api
    )
    if len(new_projects) == 0: return [] 

    save_new_projects_to_json(file_name=file_path, new_projects=parsed_projects_from_api)

    return new_projects

