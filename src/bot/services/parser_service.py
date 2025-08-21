from typing import Iterable
from aiogram.fsm.context import FSMContext

from bot.services.state_service import get_parser_state
from bot.states import Menu

from services.main import parse_kwork
from services.kwork_api_service import KworkApiBan
from services.storage_service import get_parser_delay

import asyncio

from business.models.category import CategoryData
from business.project_filter import get_new_projects


async def _toggle_parser_state(state: FSMContext) -> None:
    parser_state = await state.get_value("parser_state")
    if parser_state is None:
        parser_state = False

    parser_state = not parser_state
    await state.update_data({"parser_state": parser_state})
    await state.set_state(Menu.parsing if parser_state else Menu.menu)


async def toggle_parser(state: FSMContext) -> None:
    await _toggle_parser_state(state)
    parser_state = await get_parser_state(state)


async def run_parser(
    categories: Iterable[CategoryData], user_id: int, state: FSMContext
):
    parser_state = await get_parser_state(state)
    parsing_delay = get_parser_delay(user_id)

    while parser_state:
        parser_state = await get_parser_state(state)

        try:
            yield await parse_kwork(categories, user_id)
        except KworkApiBan:
            await _toggle_parser_state(state)
            yield KworkApiBan
            return

        await asyncio.sleep(parsing_delay)
