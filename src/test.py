import asyncio
from pathlib import Path

from parser.project_filter import get_new_projects
from parser.kwork_api_service import get_project_by_page
from parser.parser_service import parse
from parser.kwork_api_service import CategoryData


async def main():
    cats = [
        CategoryData(15, None, None), CategoryData(17, None, None), CategoryData(7, None, None),
        CategoryData(83, None, None), CategoryData(45, None, None), CategoryData(5, None, None), CategoryData(11, None, None)
    ]
    while True:
        parsed = []
        for cat in cats:
            projects = await get_project_by_page(cat)
            parsed.extend(parse([projects]))

        res = get_new_projects(Path('./test.json'), parsed)
        for p in res:
            print(f'New: {p.name}')
        await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.run(main())
