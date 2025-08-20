from business.models.category import CategoryData


def _get_query_string_by_category(category: CategoryData) -> str:
    if category.main_id is not None:
        return f'&c={category.main_id}'
    if category.attr_id is not None:
        return f'&c={category.sub_id}&attr={category.attr_id}'
    return f'&c={category.sub_id}'
