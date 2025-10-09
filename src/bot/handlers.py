import logging

from aiogram.types import ErrorEvent, Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from services.categories_parser_service import parse
from services.kwork_api_service import KworkApiBan, KworkApiError
from services.storage_service import (
    StorageServiceException,
    get_categories,
    get_parser_delay,
    save_categories,
    save_parser_delay,
)

from business.models.category import (
    TelegramCategory,
    TelegramSubCategory,
    TelegramAttr,
    CategoryData,
)

from bot.texts import SETTINGS_MENU, WELCOME_MESS, MAIN_MENU, CHOICE_CATS_MENU
from bot.exception import TelegramBotException
from bot.states import Menu
from bot.keyboards import *

from bot.services.category_service import (
    build_category_data,
    set_selected_cats,
    change_selected,
    build_selected_cats_text,
)
from bot.services.parser_service import toggle_parser, run_parser
from bot.services.state_service import (
    get_parser_state,
    get_sub_cats,
    init_menu_state,
    get_key_by_state,
)
from bot.services.message_service import build_project_message

from config import settings


router = Router()

logger = logging.getLogger(__name__)

parsed_categories = parse(settings.file_config.cats_path)
CATEGORIES_STATE_TYPE = (
    list[TelegramCategory] | list[TelegramSubCategory] | list[TelegramAttr] | None
)


@router.error(ExceptionTypeFilter(TelegramBotException))
async def error(event: ErrorEvent):
    """Отлавливает ошибки типа TelegramBotException и логгирует их"""
    user_id = None
    if event.update.callback_query is not None:
        user_id = event.update.callback_query.from_user.id
    elif (
        event.update.message is not None and event.update.message.from_user is not None
    ):
        user_id = event.update.message.from_user.id

    if user_id is not None and event.bot is not None:
        await event.bot.send_message(
            chat_id=user_id,
            text=f"Извини, произошла ошибка: {event.exception}. Попробуйте еще раз.",
        )

    logger.critical(event.exception)


@router.callback_query(F.data == "parser_toggle")
async def parser_toggle(cb: CallbackQuery, state: FSMContext):
    categories = get_categories(cb.from_user.id)
    if not categories:
        await cb.answer(
            "Сначала выбери нужные категории для парсинга."
            "Перейди в Главное меню > Настройки парсера > Выбор категории.",
            show_alert=True,
        )
        return

    await toggle_parser(state)
    parser_state = await get_parser_state(state)

    await cb.message.edit_reply_markup(reply_markup=show_parser_menu(parser_state))

    if parser_state is True:
        await cb.answer("👏 Теперь ты будешь получать новые проекты в этот чат!")

        try:
            async for new_projects in run_parser(categories, cb.from_user.id, state):
                if new_projects is KworkApiBan:
                    await cb.message.answer("❌ API временно заблокирован...")
                    await show_menu(cb.message, state)
                    break

                for project in new_projects:
                    url = f"https://kwork.ru/projects/{project.id}/view"
                    await cb.message.answer(
                        build_project_message(project), reply_markup=project_link(url)
                    )
        except KworkApiError as e:
            await cb.message.answer(f"Произошла ошибка:\n{e}")

    else:
        await cb.answer("Парсер остановлен!", show_alert=True)


@router.callback_query(Menu.parsing)
async def parsing_alert(cb: CallbackQuery):
    await cb.answer(
        "🫷Во время работы парсера нельзя ничего настраивать!"
        " Выключить парсер можно в главном меню.",
        show_alert=True,
    )


@router.message(CommandStart())
async def start(mess: Message) -> None:
    await mess.answer(
        WELCOME_MESS.format(name=mess.from_user.first_name),
        reply_markup=show_main_menu(),
    )


@router.message(F.text.contains("Главное меню"))
async def show_menu(mess: Message, state: FSMContext) -> None:
    user_cats = get_categories(mess.from_user.id)
    # category_ids = get_category_ids(mess.from_user.id)
    cats = set_selected_cats(parsed_categories, user_cats)

    await state.update_data(main_cats=cats, res=set(user_cats))

    await init_menu_state(state)
    parser_state = await get_parser_state(state)
    if parser_state is None:
        raise TelegramBotException

    await mess.answer(text=MAIN_MENU, reply_markup=show_parser_menu(parser_state))


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    parser_state = await get_parser_state(state)
    await cb.message.edit_text(MAIN_MENU, reply_markup=show_parser_menu(parser_state))


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    await cb.message.edit_text(SETTINGS_MENU, reply_markup=show_settings_parser_menu())
    await state.set_state(Menu.settings)


@router.callback_query(F.data == "settings")
async def show_settings_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    await cb.message.edit_text(SETTINGS_MENU, reply_markup=show_settings_parser_menu())
    await state.set_state(Menu.settings)


@router.callback_query(F.data == "set_time_parse")
async def set_parsing_delay(cb: CallbackQuery, state: FSMContext):
    delay = get_parser_delay(cb.from_user.id)
    await cb.message.answer(
        f"Сейчас установлено: {delay} секунд.\n"
        "Введи как часто нужно првоерять биржу, в секундах, просто число:"
    )
    await cb.answer()
    await state.set_state(Menu.set_delay)


@router.message(Menu.set_delay)
async def input_parsing_delay(mess: Message, state: FSMContext):
    if not mess.text.isdigit() or mess.text is None:
        await mess.answer("Это не число! Попробуй еще раз.")
        return
    number = int(mess.text)
    save_parser_delay(number, mess.from_user.id)

    await mess.answer("✅ Успешно сохранил!")
    await mess.answer(SETTINGS_MENU, reply_markup=show_settings_parser_menu())
    await state.set_state(Menu.settings)


@router.callback_query(Menu.settings, F.data == "choice_category")
async def choose_cat_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    user_cats = get_categories(cb.from_user.id)
    # category_ids = get_category_ids(cb.from_user.id)
    cats = set_selected_cats(parsed_categories, user_cats)

    await state.update_data(main_cats=cats, res=set(user_cats))

    await cb.message.edit_text(
        text=CHOICE_CATS_MENU.format(
            selected_cats_text=build_selected_cats_text(parsed_categories)
        ),
        reply_markup=get_category_menu(parsed_categories),
    )
    await state.set_state(Menu.choose_main_cat)


@router.callback_query(
    StateFilter(Menu.choose_main_cat, Menu.choose_sub_cat, Menu.choose_attr),
    F.data.contains("select"),
)
async def select_cat(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    id = int(cb.data.split(":")[-1])

    cats_key = await get_key_by_state(state)
    cats: CATEGORIES_STATE_TYPE = await state.get_value(cats_key)
    if cats is None:
        raise TelegramBotException(f"Нету {cats_key}")

    cats = change_selected(cats, id)
    await state.update_data({cats_key: cats})

    res: set[CategoryData] | None = await state.get_value("res")
    if res is None:
        raise TelegramBotException

    category_data = await build_category_data(state, id)

    if category_data in res:
        res.remove(category_data)
    else:
        res.add(category_data)

    await state.update_data(res=res)

    await cb.message.edit_reply_markup(reply_markup=get_category_menu(cats))


@router.callback_query(F.data == "back_cat")
async def back_cat(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    curr_state = await state.get_state()
    reply_markup = None
    text = None
    if curr_state == Menu.choose_main_cat:
        text = SETTINGS_MENU
        reply_markup = show_settings_parser_menu()
        await state.set_state(Menu.settings)
    elif curr_state == Menu.choose_sub_cat:
        text = CHOICE_CATS_MENU.format(
            selected_cats_text=build_selected_cats_text(parsed_categories)
        )
        reply_markup = get_category_menu(parsed_categories)
        await state.set_state(Menu.choose_main_cat)
    elif curr_state == Menu.choose_attr:
        sub_cats = await get_sub_cats(state)

        text = CHOICE_CATS_MENU.format(
            selected_cats_text=build_selected_cats_text(parsed_categories)
        )
        reply_markup = get_category_menu(sub_cats)
        await state.set_state(Menu.choose_sub_cat)
    else:
        raise TelegramBotException("Не перешел назад, не знаю состояния!")
    await cb.message.edit_text(text, reply_markup=reply_markup)


@router.callback_query(
    F.data == "save",
    StateFilter(Menu.choose_main_cat, Menu.choose_sub_cat, Menu.choose_attr),
)
async def save(cb: CallbackQuery, state: FSMContext):
    res: set[CategoryData] | None = await state.get_value("res")
    if res is None:
        await cb.answer("❌ Нечего сохранять!", show_alert=True)
        return

    try:
        save_categories(cb.from_user.id, res)
    except StorageServiceException as e:
        await cb.answer("Произошла ошибка!", show_alert=True)
        return

    await cb.message.edit_text(MAIN_MENU, reply_markup=show_parser_menu(False))
    await state.set_state(Menu.menu)
    await cb.answer("✅ Успешно сохранил!")


@router.callback_query(Menu.choose_main_cat, F.data.as_("id"))
async def choose_sub_cat(cb: CallbackQuery, state: FSMContext, id: str):
    await cb.answer()
    id = int(id)  # pyright: ignore

    cats = None
    for cat in parsed_categories:
        if cat.id == id:
            cats = cat.sub_categories
            break
    if cats is None:
        raise TelegramBotException

    await state.update_data(sub_cats=cats)

    await cb.message.edit_reply_markup(reply_markup=get_category_menu(cats))
    await state.set_state(Menu.choose_sub_cat)


@router.callback_query(Menu.choose_sub_cat, F.data.as_("id"))
async def choose_attr(cb: CallbackQuery, state: FSMContext, id: str):
    id = int(id)  # pyright: ignore

    await state.update_data(sub_cat_id=id)

    sub_cats_from_state: list[TelegramSubCategory] | None = await state.get_value(
        "sub_cats"
    )
    if sub_cats_from_state is None:
        raise TelegramBotException

    attrs = None
    for sub_cat in sub_cats_from_state:
        if sub_cat.id == id:
            attrs = sub_cat.attrs  # может быть пустым списком
            break

    if not attrs:
        await cb.answer("Нету атрибутов :(")
        return

    await state.update_data(attrs=attrs)

    await cb.message.edit_reply_markup(reply_markup=get_category_menu(attrs))
    await state.set_state(Menu.choose_attr)


@router.message(F.text.contains("Об авторе бота"))
async def about_author(mess: Message) -> None:
    await mess.answer("dfsd")
