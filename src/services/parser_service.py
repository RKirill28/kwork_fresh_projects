from pydantic import ValidationError

from business.models.category import ApiResponse, CategoryData

from business.models.project import *


class ParserError(Exception):
    """Ошибка парсинга"""


def _validate_and_parse(data: list[dict]) -> list[Project]:
    try:
        return [Project.model_validate(json_obj) for json_obj in data]
    except ValidationError:
        raise ParserError


def _parse_data(data: dict) -> list[dict]:
    try:
        return data["data"]["pagination"]["data"]
    except KeyError:
        raise ParserError


def run():
    pass


def _parse(data: dict) -> list[Project]:
    if not data.get("success"):
        raise ParserError
    parsed_data = _parse_data(data)

    return _validate_and_parse(parsed_data)


def _conver_to_dataclass(projects: list[Project]) -> list[ProjectData]:
    return [
        ProjectData(
            id=project.id,
            name=project.name,
            description=project.description,
            price_limit=project.price_limit,
            possible_price=project.possible_price,
            date_active=project.date_active,
            date_create=project.date_create,
            date_expire=project.date_expire,
            time_left=project.time_left,
            kwork_count=project.kwork_count,
            files=[
                FileData(fname=file.fname, size=file.size, url=file.url)
                for file in project.files
            ],
            user=UserDataclass(
                username=project.user.username,
                wants_count=project.user.data.wants_count,
                wants_hired_percent=project.user.data.wants_hired_percent,
            ),
            category=project.category,
        )
        for project in projects
    ]


def _add_category_to_projects(
    projects: list[ProjectData], category: CategoryData
) -> list[ProjectData]:
    for project in projects:
        project.category = category
    return projects


def parse(data: list[ApiResponse]) -> list[ProjectData]:
    parsed = []
    for response in data:
        parsed.extend(
            _add_category_to_projects(
                _conver_to_dataclass(_parse(response.json)), category=response.category
            )
        )
    return parsed
