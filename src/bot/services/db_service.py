import json

from pathlib import Path

from parser.kwork_api_service import CategoryData

from dataclasses import asdict, dataclass


db_file = Path('./data.json')

# @dataclass
# class CategoryData:
#     """
#     Это для теста
#     """
#     a: int
#     b: int
#     c: int


JsonDBType = dict[int, list[CategoryData]]

class JsonDBServiceException(Exception):
    """Ошибка в работе сервиса базы данных"""


def _serialize_data(data: JsonDBType) -> dict[int, list[dict[str, int]]]:
    serializated_data = {}
    for user_id, value in data.items():
        serializated_data[int(user_id)] = list()
        for cat in value:
            serializated_data[int(user_id)].append(asdict(cat))
    return serializated_data

def _deserialize_data(data: dict[int, list[dict[str, int]]]) -> JsonDBType:
    deserializated_data = {}
    for user_id, val in data.items():
        deserializated_data[int(user_id)] = list()
        for cat in val:
            deserializated_data[int(user_id)].append(CategoryData(**cat))
    return deserializated_data

def _get_json_data() -> JsonDBType:
    if not db_file.exists() or db_file.stat().st_size == 0:
        return {}

    with open(db_file.resolve(), 'r', encoding='utf-8') as f:
        try:
            json_data: dict = json.load(f)
        except json.JSONDecodeError as e:
            raise JsonDBServiceException(e)
        return _deserialize_data(json_data)

def _save_json_data(data: JsonDBType) -> None:
    with open(db_file.resolve(), 'w', encoding='utf-8') as f:
        serializated_data = _serialize_data(data)
        json.dump(serializated_data, f, indent=4, ensure_ascii=False)

def _init_user_data(json_data: JsonDBType, user_id: int) -> list[CategoryData]:
    json_data[user_id] = list()
    _save_json_data(json_data)
    return json_data[user_id]

def save_categories(cats: list[CategoryData], user_id: int) -> None:
    """Устанавливает список указанных категорий юзеру по указанному user_id"""
    json_data = _get_json_data()
    
    user_data = json_data.get(user_id)
    if user_data is None: 
        user_data = _init_user_data(json_data, user_id)

    json_data[user_id] = cats
    _save_json_data(json_data)

def get_categories(user_id: int) -> list[CategoryData]:
    """Получает список категорий по указанному user_id"""
    json_data = _get_json_data()

    user_data = json_data.get(user_id)
    if user_data is None:
        user_data = _init_user_data(json_data, user_id)

    return user_data

def get_category_ids(user_id: int) -> set[int]:
    """Получает id категорий"""
    categories_data = get_categories(user_id)
    res = set()
    for cat in categories_data:
        res.add(cat.attr_id)
        res.add(cat.sub_id)
        res.add(cat.main_id)
    if None in res:
        res.remove(None)
    return res



    

if __name__ == '__main__':
    save_categories([CategoryData(5, 2,2)], 23423)
    user_data = get_categories(23423)
    print(user_data)
