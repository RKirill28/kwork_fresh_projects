import json

from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from business.models.project import ProjectData

from config import settings


last_project_file = settings.file_config.last_project_path


class SaverError(Exception):
    """Ошибка сохранения файла json"""

def _serialize_datetime_to_iso(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f'Object of type {obj.__class__.__name__} '
                    f'is not JSON serializable')

def _datetime_hook(obj):
    for k, v in obj.items():
        if isinstance(v, str):
            try:
                obj[k] = datetime.fromisoformat(v)
            except ValueError:
                pass
    return obj

def _add_project_ids_to_json(file_name: Path, projects: list[ProjectData]) -> None:
    with open(file_name.resolve(), 'r') as f:
        projects_from_json: list[int] = json.load(f)

    for project in projects:
        projects_from_json.append(project.id) 

    with open(file_name.resolve(), 'w', encoding='utf-8') as f:
        json.dump(projects_from_json, f, default=_serialize_datetime_to_iso, indent=4, ensure_ascii=False)

def save_last_project_by_user_id(user_id: int, project: ProjectData) -> None:
    with open(last_project_file.resolve(), 'r', encoding='utf-8') as f:
        data = json.load(f)
        data[str(user_id)] = asdict(project)

    with open(last_project_file.resolve(), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, default=_serialize_datetime_to_iso, ensure_ascii=False)

def get_last_project_by_user_id(user_id: int) -> ProjectData | None:
    with open(last_project_file.resolve(), 'r', encoding='utf-8') as f:
        try:
            data: dict = json.load(f, object_hook=_datetime_hook)
        except json.JSONDecodeError:
            raise SaverError(f'Ошибка чтения {last_project_file.name}')

    user_data: dict | None = data.get(str(user_id))
    if user_data is None:
        return

    last_project = ProjectData(**user_data) 
    return last_project

def init_json_file() -> None:
    if not last_project_file.exists():
        last_project_file.parent.mkdir(parents=True, exist_ok=True)  # создаём папку, если нет
        with open(last_project_file.resolve(), "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        return

    try:
        with open(last_project_file.resolve(), "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        with open(last_project_file.resolve(), "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

def save_new_projects_to_json(file_name: Path, new_projects: list[ProjectData]) -> None:
    """Перебирает data и сохраняет только новые
    """
    _add_project_ids_to_json(file_name, new_projects)
