import json

from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from typing import Iterable

from config import settings

from business.models.project import ProjectData
from business.models.category import CategoryData


categories_file = settings.file_config.user_cats_path
storage_file = settings.file_config.user_data

CATS_JSON_INPUT_TYPE = dict[int, list[CategoryData]]
CART_JSON_OUTPUT_TYPE = dict[str, list[dict[str, int]]]


class StorageServiceException(Exception):
    """Ошибка в работе сервиса хранилища"""


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

def init_json_file(file: Path) -> None:
    """
    Инициализиурет указанный json файл
    """
    if not file.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file.resolve(), "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return

    try:
        with open(file.resolve(), "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        with open(file.resolve(), "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

def _get_user_data(user_id: int) -> dict:
    json_data = _get_storage()
    return json_data.get(str(user_id), {})

def _save_user_data(user_id: int, user_data: dict) -> None:
    json_data = _get_storage()
    json_data[str(user_id)] = user_data
    _save_storage(json_data)

def _get_storage() -> dict:
    with open(storage_file.resolve(), 'r', encoding='utf-8') as f:
        try:
            data: dict = json.load(f, object_hook=_datetime_hook)
            return data
        except json.JSONDecodeError:
            raise StorageServiceException(f'Ошибка чтения {storage_file.name}')

def _save_storage(storage: dict) -> None:
    with open(storage_file.resolve(), 'w', encoding='utf-8') as f:
        json.dump(storage, f, indent=4, default=_serialize_datetime_to_iso, ensure_ascii=False)

def save_last_project_by_user_id(user_id: int, project: ProjectData) -> None:
    """
    Сохраняет указанный проект в БД
    """
    user_data = _get_user_data(user_id)
    user_data['project'] = asdict(project)
    _save_user_data(user_id, user_data)

def get_last_project_by_user_id(user_id: int) -> ProjectData | None:
    """
    Возвращает последний спарсенный проект из БД, если нету возвращает None
    """
    user_data = _get_user_data(user_id)

    project = user_data.get('project')
    if project is None: 
        return

    return ProjectData(**project) 

def get_categories(user_id: int) -> set[CategoryData]:
    """
    Получает set категорий из БД 
    """
    user_data = _get_user_data(user_id)

    cats: list[dict] | None = user_data.get('cats')
    if cats is None: return set()
    
    return {CategoryData(**cat_dict) for cat_dict in cats}

def get_category_ids(user_id: int) -> set[int]:
    cats = get_categories(user_id)

    res = set()
    for cat in cats:
        res.add(cat.main_id)
        if cat.attr_id is None:
            res.add(cat.sub_id)
        res.add(cat.attr_id)

    if None in res:
        res.remove(None)
    return res

def save_categories(user_id: int, cats: Iterable[CategoryData]) -> None:
    """
    Сохраняет список категорий в БД
    """
    user_data = _get_user_data(user_id)
    user_data['cats'] = [
        {
            'main_id': cat.main_id,
            'sub_id': cat.sub_id,
            'attr_id': cat.attr_id
        } 
        for cat in cats
    ]

    _save_user_data(user_id, user_data)

def get_parser_delay(user_id: int) -> int:
    """
    Возвращает parsing delay из БД, если не установлен, то возвращает 60
    """
    user_data = _get_user_data(user_id)
    return user_data.get('parsing_delay', 60)

def save_parser_delay(delay: int, user_id: int) -> None:
    """
    Сохраняет указанный parsing delay в БД
    """
    user_data = _get_user_data(user_id)
    user_data['parsing_delay'] = delay
    _save_user_data(user_id, user_data)
