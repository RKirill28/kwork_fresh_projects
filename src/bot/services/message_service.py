from business.models.project import ProjectData


def new_project_message(project: ProjectData):
    return f"""
    · Новый проект ·
    ID <blockquote>· {project.id}</blockquote>
    Название <blockquote>· {project.name}</blockquote>
    Описание <blockquote>· {project.description}</blockquote>
    Желательная цена <blockquote>· {project.possible_price}</blockquote>
    Максимальная цена <blockquote>· {project.price_limit}</blockquote>
    Осталось времени <blockquote>· {project.time_left}</blockquote>
    """
