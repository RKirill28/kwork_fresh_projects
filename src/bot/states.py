from aiogram.fsm.state import State, StatesGroup


class ChooseCat(StatesGroup):
    main_cats: State = State()
    sub_cats: State = State()
    attrs: State = State()


class Menu(StatesGroup):
    menu: State = State()
    parsing: State = State()
    settings: State = State()
    set_delay: State = State()
    choose_main_cat: State = State()
    choose_sub_cat: State = State()
    choose_attr: State = State()
