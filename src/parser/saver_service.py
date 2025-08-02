from datetime import datetime
from io import TextIOWrapper

import json
from pathlib import Path
from typing import TextIO
from parser.parser_service import Project, ProjectData
from dataclasses import asdict


class SaverError(Exception):
    """Ошибка сохранения файла json"""


def _serialize_datetime_to_iso(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} '
                    f'is not JSON serializable')

def _add_projects_to_json(file_name: Path, projects: list[ProjectData]) -> None:
    with open(file_name.resolve(), 'r') as f:
        projects_from_json = json.load(f)

    for project in projects:
        projects_from_json[str(project.id)] = asdict(project)

    with open(file_name.resolve(), 'w', encoding='utf-8') as f:
        json.dump(projects_from_json, f, default=_serialize_datetime_to_iso, indent=4, ensure_ascii=False)

def get_new_projects(file_name: Path, parsed_data: list[ProjectData]) -> list[ProjectData]:
    """Получает только новые элементы(тех что нету в json) из parsed_data"""
    with open(file_name.resolve(), 'r', encoding='utf-8') as f:
        projects_from_json = json.load(f)
    projects = {str(project.id):project for project in parsed_data}
    
    new_projects = []
    for id, project in projects.items():
        if not id in projects_from_json:
            print('Нету')
            new_projects.append(project) 
    return new_projects

def save_new_projects_to_json(file_name: Path, new_projects: list[ProjectData]) -> None:
    """Перебирает data и сохраняет только новые
    """
    _add_projects_to_json(file_name, new_projects)
