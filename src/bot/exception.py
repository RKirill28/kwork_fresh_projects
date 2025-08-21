class TelegramBotException(Exception):
    """Это ошибка в работе телеграм бота"""


class StateWorkException(Exception):
    """Ошибка при работе с FSMContext"""
