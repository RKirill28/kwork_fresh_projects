from typing import Iterable
from business.models.project import ProjectData
from services.storage_service import (
    get_last_project_by_user_id,
    save_last_project_by_user_id,
)


class ProjectFilterException(Exception):
    """Ошибка в работе фильтра проектов"""


def get_new_projects(
    parsed_data: Iterable[ProjectData], user_id: int
) -> list[ProjectData]:
    """Получает только новые проекты из спарсенных"""
    sorted_projects: list[ProjectData] = sorted(
        parsed_data, key=lambda k: k.date_active
    )

    lp = get_last_project_by_user_id(user_id)
    if lp is None:
        save_last_project_by_user_id(user_id, sorted_projects[-1])
        return []

    if sorted_projects[-1].id == lp.id:
        return []

    save_last_project_by_user_id(user_id, sorted_projects[-1])

    new_projects = []
    for project in sorted_projects:
        p_id = project.id
        if project.date_active > lp.date_active and p_id != lp.id:
            new_projects.append(project)
    return new_projects
