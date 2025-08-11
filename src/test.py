import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, TelegramObject
from aiogram.types.error_event import ErrorEvent
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode, parse_mode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings

from parser.categories_parser_service import TelegramAttr, TelegramCategory, TelegramSubCategory, parse 
from parser.kwork_api_service import CategoryData

from bot.services.state_service import add_data_to_state
from bot.exception import TelegramBotException

from pathlib import Path


bot = Bot(
	token=settings.bot_config.token,
	default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(storage=MemoryStorage())

logger_format = '%(levelname)s:%(name)s:%(funcName)s() - %(message)s'
logging.basicConfig(level=logging.INFO, format=logger_format)

parsed_categories = parse(Path('./categories.json'))


class Menu(StatesGroup):
    main_menu: State = State()
    choose_main_cat: State = State()
    choose_sub_cat: State = State()
    choose_attr: State = State()

class SelectCategory(CallbackData, prefix='select'):
    main_id: int | None = None
    sub_id: int | None = None
    attr_id: int | None = None

def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Select cat', callback_data='choose_cat')]]
    )

def change_main_cat_selected(cats: list[TelegramCategory], id: int):
    for cat in cats:
        if cat.id == id:
            cat.selected = not cat.selected
    return cats

def get_category_menu(cats: list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for cat in cats:
        select_cb_data = SelectCategory(
            main_id=cat.id
        )

        if isinstance(cat, (TelegramCategory, TelegramSubCategory)):
            builder.row(
                InlineKeyboardButton(
                    text=f' + {cat.name}' if cat.selected else cat.name,
                    callback_data=select_cb_data.pack()
                ),
                InlineKeyboardButton(text=' -> ', callback_data=f'{cat.id}')
            )    
        else:
            builder.row(
                InlineKeyboardButton(
                    text=f' + {cat.name}' if cat.selected else cat.name,
                    callback_data=select_cb_data.pack()
                ),
            )    
    builder.row(
        InlineKeyboardButton(text='<---<---<', callback_data='back_cat'),
        InlineKeyboardButton(text='Сохранить и в гл. меню', callback_data='save')
    )

    return builder.as_markup()
            
@dp.message(Command('show'))
async def show_menu(message: Message, state: FSMContext):
    await message.answer('Hello')
    await state.set_state(Menu.main_menu)

    await state.update_data(da=5)
    da = await state.get_data()
    print(da)
    await message.answer(
        text='Menu',
        reply_markup=get_main_menu()
    )

@dp.callback_query(F.data == 'choose_cat')
async def choose_cat_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    await add_data_to_state(state, 'main_cats', parsed_categories)
    await add_data_to_state(state, 'cats_set', set())
    await add_data_to_state(state, 'res', set())

    await cb.message.answer(
        text='categories',
        reply_markup=get_category_menu(parsed_categories)
    )
    await state.set_state(menu.choose_main_cat)

async def get_cats_key(state: FSMContext):
    curr_state = await state.get_state()
    if curr_state == Menu.choose_main_cat.state:
        return 'main_cats'
    elif curr_state == Menu.choose_sub_cat.state:
        return 'sub_cats'
    elif curr_state == Menu.choose_attr.state:
        return 'attrs'
    else:
        raise TelegramBotException('Не удалось получить ключ категорий')


@dp.callback_query(SelectCategory.filter())
async def select_cat(cb: CallbackQuery, state: FSMContext, callback_data: SelectCategory):
    await cb.answer()

    cats_key = await get_cats_key(state)

    cats: list[TelegramCategory] = await state.get_value(cats_key)
    cats = change_main_cat_selected(cats, callback_data.main_id)

    cats_set: set|None = await state.get_value('cats_set')
    if cats_set is None: raise TelegramBotException
    
    if callback_data.main_id in cats_set:
        cats_set.remove(callback_data.main_id)
    else:
        cats_set.add(callback_data.main_id)
    await state.update_data(cats_set=cats_set)
    
    await add_data_to_state(state, cats_key, cats)

    res: set | None = await state.get_value('res')
    if res is None: raise TelegramBotException

    curr_state = await state.get_state()
    if curr_state == Menu.choose_main_cat.state:
        cat = CategoryData(callback_data.main_id, None, None)
    elif curr_state == Menu.choose_sub_cat.state:
        cat = CategoryData(None, callback_data.main_id, None)
    elif curr_state == Menu.choose_attr.state:
        sub_cat_id = await state.get_value('sub_cat_id')
        if sub_cat_id is None: TelegramBotException
        cat = CategoryData(None, sub_cat_id, callback_data.main_id) 
    else: cat = None

    if cat is None: raise TelegramBotException

    if cat in res:
        res.remove(cat)
    else:
        res.add(cat)

    await state.update_data(res=res)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )

@dp.callback_query(F.data == 'back_cat')
async def back_cat(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    curr_state = await state.get_state()
    reply_markup = None
    if curr_state == Menu.choose_main_cat:
        reply_markup = get_main_menu()
        await state.set_state(Menu.main_menu)
    elif curr_state == Menu.choose_sub_cat:
        cats = await state.get_value('main_cats')
        reply_markup = get_category_menu(cats)
        await state.set_state(Menu.choose_main_cat)
    elif curr_state == Menu.choose_attr:
        cats = await state.get_value('sub_cats')
        reply_markup = get_category_menu(cats)
        await state.set_state(Menu.choose_sub_cat)
    else:
        raise TelegramBotException('Не перешел назад, не знаю состояния!')
    await cb.message.edit_reply_markup(
        reply_markup=reply_markup
    )

@dp.callback_query(Menu.choose_main_cat, F.data=='save')
@dp.callback_query(Menu.choose_sub_cat, F.data=='save')
@dp.callback_query(Menu.choose_attr, F.data=='save')
async def save(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    res = await state.get_value('res')
    print(res)

@dp.callback_query(Menu.choose_main_cat, F.data.as_('id'))
async def choose_sub_cat(cb: CallbackQuery, state: FSMContext, id: str):
    await cb.answer()
    id = int(id)

    cats = None
    for cat in parsed_categories:
        if cat.id == id:
            cats = cat.sub_categories
            break
    if cats is None: raise TelegramBotException
    
    await add_data_to_state(state, 'sub_cats', cats)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )
    await state.set_state(Menu.choose_sub_cat)

@dp.callback_query(Menu.choose_sub_cat, F.data.as_('id'))
async def choose_attr(cb: CallbackQuery, state: FSMContext, id: str):
    await cb.answer()
    print(id)
    id = int(id) # жто sub_cat_id
    
    await add_data_to_state(state, 'sub_cat_id', id)

    cats_key = await get_cats_key(state)
    sub_cats: list[TelegramSubCategory] = await state.get_value(cats_key)

    cats = None
    for sub_cat in sub_cats:
        if sub_cat.id == id:
            cats = sub_cat.attrs
            break
    if cats is None: raise TelegramBotException(f'Не удалось найти аттрибуты для подкатегории {id}')

    await add_data_to_state(state, 'attrs', cats)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )
    await state.set_state(Menu.choose_attr)






async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
	asyncio.run(main())
