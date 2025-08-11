from aiogram.fsm.context import FSMContext

from parser import parse_kwork
from bot.services.state_service import get_parser_state
from bot.states import Menu

import asyncio


async def _toggle_parser_state(state: FSMContext) -> None:
    parser_state = await state.get_value('parser_state')
    if parser_state is None: return 
    parser_state = not parser_state
    await state.update_data({'parser_state': parser_state})
    await state.set_state(Menu.parsing if parser_state else Menu.menu)

async def toggle_parser(state: FSMContext) -> None:
    await _toggle_parser_state(state)
    parser_state = await get_parser_state(state)
         
