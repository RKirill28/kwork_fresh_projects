from datetime import datetime

from dataclasses import dataclass
from typing import NamedTuple

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from parser.kwork_api_service import ApiResponse, CategoryData


class ParserError(Exception):
    """Ошибка парсинга"""

class ParsedJson(NamedTuple):
    data: list[dict]
    category: CategoryData

class UserData(BaseModel):
    wants_hired_percent: int
    wants_count: int

class User(BaseModel):
    username: str
    data: UserData

class File(BaseModel):
    fname: str
    size: int
    url: str

class Project(BaseModel):
    id: int
    name: str
    description: str
    price_limit: int = Field(alias='priceLimit')
    possible_price: int = Field(alias='possiblePriceLimit')
    date_create: datetime
    date_expire: datetime
    time_left: str = Field(alias='timeLeft')
    kwork_count: int
    files: list[File] = []
    user: User
    category: CategoryData | None = None

@dataclass
class FileData:
    fname: str
    size: int
    url: str

@dataclass
class UserDataclass:
    username: str
    wants_hired_percent: int
    wants_count: int

@dataclass
class ProjectData:
    id: int
    name: str
    description: str
    price_limit: int
    possible_price: int
    date_create: datetime
    date_expire: datetime
    time_left: str
    kwork_count: int
    user: UserDataclass
    category: CategoryData | None
    files: list[FileData]


def _validate_and_parse(data: list[dict]) -> list[Project]:
    try:
        return [Project.model_validate(json_obj) for json_obj in data]
    except ValidationError:
        raise ParserError

def _parse_data(data: dict) -> list[dict]:
    try:
        return data['data']['pagination']['data']
    except KeyError:
        raise ParserError

def run(): pass

def _parse(data: dict) -> list[Project]:
    if not data.get('success'): raise ParserError
    parsed_data = _parse_data(data)

    return _validate_and_parse(parsed_data)

def _conver_to_dataclass(projects: list[Project]) -> list[ProjectData]:
    return [ProjectData(
        id=project.id,
        name=project.name,
        description=project.description,
        price_limit=project.price_limit,
        possible_price=project.possible_price,
        date_create=project.date_create,
        date_expire=project.date_expire,
        time_left=project.time_left,
        kwork_count=project.kwork_count,
        files=[FileData(fname=file.fname, size=file.size, url=file.url) for file in project.files],
        user=UserDataclass(
            username=project.user.username, 
            wants_count=project.user.data.wants_count, 
            wants_hired_percent=project.user.data.wants_hired_percent
        ),
        category=project.category
    ) for project in projects]

def _add_category_to_projects(projects: list[ProjectData], category: CategoryData) -> list[ProjectData]:
    for project in projects:
        project.category = category
    return projects

def parse(data: list[ApiResponse]) -> list[ProjectData]:
    parsed = []
    for response in data:
        parsed.extend(
            _add_category_to_projects(
                _conver_to_dataclass(_parse(response.json)),
                category=response.category
            )
        )
    return parsed
