from telebot import ExceptionHandler
from telegram_logger_bot import TelegramLoggerBot


class MyExceptionHandler(ExceptionHandler):
    def __init__(self, admin_id: int, logger: TelegramLoggerBot):
        self.admin_id = admin_id
        self.logger = logger
        super().__init__()

    def handle(self, exception):
        self.logger.post(method='sendMessage', err=exception,
                         chat_id=self.admin_id)
        return True


class NoEnvironmentVariable(Exception):
    def __init__(self, message: str = 'No environment variable'):
        self.message = message
        super().__init__(self.message)


class MessageTextEmpty(Exception):
    def __init__(self, message: str = 'Message text is empty'):
        self.message = message
        super().__init__(self.message)


class NoPhoto(Exception):
    def __init__(self, message: str = 'There is no photo'):
        self.message = message
        super().__init__(self.message)
