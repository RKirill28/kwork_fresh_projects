from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class InitialMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        state: FSMContext | None = data.get('state')
        
        # if state is not None:
        #     await init_cats_set(state)
        #     await init_category_list(state)

        return await handler(event, data)

