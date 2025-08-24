from business.models.project import ProjectData


def build_project_message(project: ProjectData):
    return f"""
    · Новый проект ·
    ID <blockquote>· {project.id}</blockquote>
    Название <blockquote>· {project.name}</blockquote>
    Описание <blockquote>· {_format_project_description(project.description)}</blockquote>
    Желательная цена <blockquote>· {project.price_limit}</blockquote>
    Максимальная цена <blockquote>· {project.possible_price}</blockquote>
    Осталось времени <blockquote>· {project.time_left}</blockquote>

    Создано: {project.date_create.strftime("%Y-%m-%d %H:%M:%S")}
    Актививровано: {project.date_active.strftime("%Y-%m-%d %H:%M:%S")}
    """


def _format_project_description(project_description: str) -> str:
    markup = {"&bull;": "· ", "&mdash;": "—"}
    for tag, translate in markup.items():
        project_description = project_description.replace(tag, translate)
    return project_description
