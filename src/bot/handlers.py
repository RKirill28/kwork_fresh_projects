import logging
import asyncio
from pathlib import Path

from aiogram.types import ErrorEvent, Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext

from parser.categories_parser_service import parse, TelegramCategory, TelegramSubCategory, TelegramAttr
from parser.kwork_api_service import CategoryData
from parser import parse_kwork

from bot.messages import WELCOME_MESS
from bot.exception import TelegramBotException 
from bot.services.state_service import get_parser_state, init_menu_state 
from bot.states import Menu
from bot.middlewares import InitialMiddleware
from bot.keyboards import *
from bot.services.db_service import JsonDBServiceException, get_categories, get_category_ids, save_categories
from bot.services.category_service import build_category_data, set_selected_cats
from bot.services.parser_service import toggle_parser

from config import settings


router = Router()
router.callback_query.middleware(InitialMiddleware())

logger = logging.getLogger(__name__)

parsed_categories = parse(settings.file_config.cats_path)
CATEGORY_FROM_STATE = list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr] | None 
TELEGRAM_CATEGORIES_TYPE = list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr]


@router.error(ExceptionTypeFilter(TelegramBotException))
async def error(event: ErrorEvent):
    """Отлавливает ошибки типа TelegramBotException и логгирует их"""
    user_id = None
    if event.update.callback_query is not None:
        user_id = event.update.callback_query.from_user.id
    elif event.update.message is not None and event.update.message.from_user is not None:
        user_id = event.update.message.from_user.id

    if user_id is not None and event.bot is not None:
        await event.bot.send_message(
	        chat_id=user_id,
	        text=f'Извините, произошла ошибка: {event.exception}. Попробуйте еще раз.'
        )

    logger.critical(event.exception)

@router.callback_query(F.data == 'parser_toggle')
async def parser_toggle(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException('Нету Message')

    await toggle_parser(state)

    parser_state = await get_parser_state(state)

    await cb.message.edit_reply_markup(
        reply_markup=show_parser_menu(parser_state)
    )
    
    categories = await state.get_value('res')
    if categories is None:
        await cb.answer('Ты не установил какие категории парсить. Сделай это в настройках!', show_alert=True)
        return

    if parser_state is True: 
        await cb.answer('👏 Теперь ты будешь получать новые проекты в этот чат!')

    while parser_state:
        print('жду')
        parser_state = await get_parser_state(state)
        new_projects = await parse_kwork(Path('./projects.json'), categories)
        for project in new_projects:
            await cb.message.answer(
                text='НОВЫЙ ПРОЕКТ!\n'
                    f'<b>Название: <u>{project.name}</u></b>'
            )
        await asyncio.sleep(10)

@router.callback_query(Menu.parsing)
async def parsing_alert(cb: CallbackQuery):
    await cb.answer(
        'Извините, но во время работы парсера нельзя нечего настраивать!'
        'Чтобы изменить конфигурацию парсера, выключите его в главном меню.',
        show_alert=True
    )

@router.message(CommandStart())
async def start(mess: Message) -> None:
    if not mess.from_user: raise TelegramBotException
    await mess.answer(
        WELCOME_MESS.format(name=mess.from_user.first_name),
        reply_markup=show_main_menu()
    )

@router.message(F.text.contains('Главное меню'))
async def show_menu(mess: Message, state: FSMContext) -> None:
    if not mess.from_user: raise TelegramBotException

    await init_menu_state(state)
    parser_state = await get_parser_state(state)
    if parser_state is None: raise TelegramBotException

    await mess.answer(
        text='Ты в главной меню, выбери действие:',
        reply_markup=show_parser_menu(parser_state)
    )

@router.callback_query(F.data == 'back_to_menu') 
async def back_to_menu(cb: CallbackQuery, state: FSMContext): 
    await cb.answer() 
    if not isinstance(cb.message, Message): raise TelegramBotException('Нету Message') 

    parser_state = await get_parser_state(state) 
    await cb.message.edit_reply_markup(
        reply_markup=show_parser_menu(parser_state)
    ) 

@router.callback_query(F.data == 'back_to_settings') 
async def back_to_settings(cb: CallbackQuery, state: FSMContext): 
    await cb.answer() 
    if not isinstance(cb.message, Message): raise TelegramBotException 

    await cb.message.edit_reply_markup(
        reply_markup=show_settings_parser_menu()
    )
    await state.set_state(Menu.settings)

@router.callback_query(F.data == 'settings')
async def show_settings_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException 

    await cb.message.edit_reply_markup(
        reply_markup=show_settings_parser_menu()
    )
    await state.set_state(Menu.settings)

@router.callback_query(Menu.settings, F.data == 'choice_category')
async def choose_cat_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException('Нету Message')

    user_cats = get_categories(cb.from_user.id)
    category_ids = get_category_ids(cb.from_user.id)
    cats = set_selected_cats(parsed_categories, category_ids)
    
    await state.update_data(main_cats=cats, cats_set=cats, res=set(user_cats))

    await cb.message.answer(
        text='categories',
        reply_markup=get_category_menu(parsed_categories)
    )
    await state.set_state(Menu.choose_main_cat)

async def get_cats_key(state: FSMContext):
    """Получаю ключ в зависимости от состояния"""
    curr_state = await state.get_state()
    if curr_state == Menu.choose_main_cat.state:
        return 'main_cats'
    elif curr_state == Menu.choose_sub_cat.state:
        return 'sub_cats'
    elif curr_state == Menu.choose_attr.state:
        return 'attrs'
    else: raise TelegramBotException('Не удалось получить ключ категорий') 

def change_main_cat_selected(cats: TELEGRAM_CATEGORIES_TYPE, id: int):
    for cat in cats:
        if cat.id == id:
            cat.selected = not cat.selected
    return cats

@router.callback_query(
    StateFilter(Menu.choose_main_cat, Menu.choose_sub_cat, Menu.choose_attr),
    F.data.contains('select')
)
async def select_cat(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException
        
    id = int(cb.data.split(':')[-1])

    cats_key = await get_cats_key(state)
    cats: CATEGORY_FROM_STATE = await state.get_value(cats_key)
    if cats is None: raise TelegramBotException(f'Нету {cats_key}')

    cats = change_main_cat_selected(cats, id)
    await state.update_data({cats_key: cats})

    res: set[CategoryData] | None = await state.get_value('res')
    if res is None: raise TelegramBotException

    category_data = await build_category_data(state, id)

    if category_data in res: res.remove(category_data)
    else: res.add(category_data)

    await state.update_data(res=res)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )

@router.callback_query(F.data == 'back_cat')
async def back_cat(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException

    curr_state = await state.get_state()
    reply_markup = None
    if curr_state == Menu.choose_main_cat:
        reply_markup = show_parser_menu(False)
        await state.set_state(Menu.menu)
    elif curr_state == Menu.choose_sub_cat:
        reply_markup = get_category_menu(parsed_categories)
        await state.set_state(Menu.choose_main_cat)
    elif curr_state == Menu.choose_attr:
        cats: list[TelegramSubCategory] | None = await state.get_value('sub_cats')
        if cats is None: raise TelegramBotException

        reply_markup = get_category_menu(cats)

        await state.set_state(Menu.choose_sub_cat)
    else:
        raise TelegramBotException('Не перешел назад, не знаю состояния!')
    await cb.message.edit_reply_markup(
        reply_markup=reply_markup
    )

@router.callback_query(
    F.data == 'save',
    StateFilter(Menu.choose_main_cat, Menu.choose_sub_cat, Menu.choose_attr)
)
async def save(cb: CallbackQuery, state: FSMContext):
    if not isinstance(cb.message, Message): raise TelegramBotException('Нету Message')

    res: set[CategoryData] | None = await state.get_value('res')
    if res is None:
        await cb.answer('❌ Нечего сохранять!')
        return

    print('Для сохранения вот такой вот сет: ', res)
    try:
        save_categories(list(res), cb.from_user.id)
    except JsonDBServiceException as e:
        await cb.answer('Произошла ошибка!')
        return

    await cb.message.edit_reply_markup(
        reply_markup=show_parser_menu(False)
    )
    await state.set_state(Menu.menu)

    await cb.answer('✅ Успешно сохранил!')

    
@router.callback_query(Menu.choose_main_cat, F.data.as_('id'))
async def choose_sub_cat(cb: CallbackQuery, state: FSMContext, id: str):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException

    id = int(id)

    cats = None
    for cat in parsed_categories:
        if cat.id == id:
            cats = cat.sub_categories
            break
    if cats is None: raise TelegramBotException
    
    # await add_data_to_state(state, 'sub_cats', cats)
    await state.update_data(sub_cats=cats)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )
    await state.set_state(Menu.choose_sub_cat)

@router.callback_query(Menu.choose_sub_cat, F.data.as_('id'))
async def choose_attr(cb: CallbackQuery, state: FSMContext, id: str):
    await cb.answer()
    if not isinstance(cb.message, Message): raise TelegramBotException

    id = int(id) # жто sub_cat_id
    
    # await add_data_to_state(state, 'sub_cat_id', id)
    await state.update_data(sub_cat_id=id)

    cats_key = await get_cats_key(state)
    if cats_key != 'sub_cats': raise TelegramBotException

    sub_cats: CATEGORY_FROM_STATE = await state.get_value(cats_key)
    if sub_cats is None: raise TelegramBotException
    if not isinstance(sub_cats[0], TelegramSubCategory): raise TelegramBotException
    sub_cats: list[TelegramSubCategory]

    cats = None
    for sub_cat in sub_cats:
        if sub_cat.id == id:
            cats = sub_cat.attrs
            break
    if cats is None: raise TelegramBotException(f'Не удалось найти аттрибуты для подкатегории {id}')

    # await add_data_to_state(state, 'attrs', cats)
    await state.update_data(attrs=cats)

    await cb.message.edit_reply_markup(
        reply_markup=get_category_menu(cats)
    )
    await state.set_state(Menu.choose_attr)

@router.message(F.text.contains('Об авторе бота'))
async def about_author(mess: Message) -> None:
    if not mess.from_user: raise TelegramBotException
    await mess.answer('dfsd')

