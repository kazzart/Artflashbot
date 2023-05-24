import os
import glob
from dotenv import load_dotenv

import requests
import telebot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from telegram_logger_bot import TelegramLoggerBot
from exceptions import MyExceptionHandler, NoEnvironmentVariable, MessageTextEmpty, NoPhoto


if __name__ == "__main__":
    load_dotenv()
    TOKEN: str | None = os.getenv('TELEGRAM_BOT_TOKEN')
    LOG_TOKEN: str | None = os.getenv('TELEGRAM_LOGGER_BOT_TOKEN')
    ADMIN_ID_STR: str | None = os.getenv('ADMIN_ID_STR')
    ADMIN_ID_STR_2: str | None = os.getenv('ADMIN_ID_STR_2')
    ADMIN_ID_STR_3: str | None = os.getenv('ADMIN_ID_STR_3')
    ADMIN_ID_STR_4: str | None = os.getenv('ADMIN_ID_STR_4')
    if TOKEN is None:
        raise NoEnvironmentVariable('No telegram bot token')
    if LOG_TOKEN is None:
        raise NoEnvironmentVariable('No telegram logger bot token')
    if ADMIN_ID_STR is None:
        raise NoEnvironmentVariable('No admin id')
    if ADMIN_ID_STR_2 is None:
        raise NoEnvironmentVariable('No admin id')
    if ADMIN_ID_STR_3 is None:
        raise NoEnvironmentVariable('No admin id')
    if ADMIN_ID_STR_4 is None:
        raise NoEnvironmentVariable('No admin id')

    BASE_URL: str = 'https://bot.telegram.org'
    ADMIN_ID: int
    ADMIN_ID_2: int
    ADMIN_ID_3: int
    ADMIN_ID_4: int
    logger: TelegramLoggerBot
    exception_handler: MyExceptionHandler
    admins: set[int]
    clients: set[int]
    bot: telebot.TeleBot
    intro: str
    welcome: str
    calendar_text: str
    flag_1: bool
    num_calendars: int

    ADMIN_ID = int(ADMIN_ID_STR)
    ADMIN_ID_2 = int(ADMIN_ID_STR_2)
    ADMIN_ID_3 = int(ADMIN_ID_STR_3)
    ADMIN_ID_4 = int(ADMIN_ID_STR_4)
    logger = TelegramLoggerBot(LOG_TOKEN, BASE_URL)
    exception_handler = MyExceptionHandler(ADMIN_ID, logger)
    intro = 'Добро пожаловать!'
    welcome = 'Это бот для присылания календаря'
    calendar_text = 'Подпись к календарю'
    flag_1 = False
    num_calendars = 0

    admins = {ADMIN_ID, ADMIN_ID_2, ADMIN_ID_3, ADMIN_ID_4}
    clients = {ADMIN_ID, ADMIN_ID_2, ADMIN_ID_3, ADMIN_ID_4}

    bot = telebot.TeleBot(TOKEN, exception_handler=exception_handler)

    @bot.message_handler(commands=['start'])
    def send_welcome(message: Message):
        idx: int = message.from_user.id
        if idx not in clients:
            clients.add(idx)
        else:
            bot.send_message(idx, 'Я тебя уже знаю')
        bot.send_message(idx, intro)
        print(idx)

    @bot.message_handler(commands=['stop'])
    def send_goodbye(message: Message):
        idx: int = message.from_user.id
        clients.remove(idx)
        bot.send_message(idx, 'Пока(')

    @bot.message_handler(commands=['getcalendar'])
    def get_calendar(message: Message):
        try:
            bot.send_chat_action(message.chat.id, 'upload_photo')
            bot.send_media_group(message.chat.id, [telebot.types.InputMediaPhoto(
                open(f'calendar_{1 + i}.jpg', 'rb')) for i, _ in enumerate(glob.glob("*.jpg"))])
            bot.send_message(message.chat.id, calendar_text)
        except FileNotFoundError:
            bot.send_message(message.chat.id, 'Календарь не установлен')

    @bot.message_handler(commands=['startsetcalendar'])
    def start_set_calendar(message: Message):
        global flag_1, num_calendars
        flag_1 = True
        for file in glob.glob("*.jpg"):
            os.remove(file)
        num_calendars = 0

    @bot.message_handler(commands=['stopsetcalendar'])
    def stop_set_calendar(message: Message):
        global flag_1
        idx: int = message.from_user.id
        flag_1 = False
        bot.send_message(idx, 'Введите подпись')
        bot.register_next_step_handler_by_chat_id(
            idx, handle_new_calendar)

    @bot.message_handler(content_types=['photo'])
    def add_calendar(message: Message):
        global num_calendars
        idx: int = message.from_user.id
        if idx in admins and message.chat.type == 'private':
            if flag_1:
                if message.photo is not None:
                    print('message.photo =', message.photo)
                    file_id = message.photo[-1].file_id
                    print('file_id =', file_id)
                    file_info = bot.get_file(file_id)
                    print('file.file_path =', file_info.file_path)
                    downloaded_file = bot.download_file(file_info.file_path)

                    with open(f"calendar_{1 + num_calendars}.jpg", 'wb') as new_file:
                        new_file.write(downloaded_file)

                    num_calendars += 1
                else:
                    raise NoPhoto('Can\'t set calendar')
        elif message.chat.type == 'private':
            bot.send_message(idx,
                             'Только админ может менять календарь')

    def handle_new_calendar(message: Message):
        global calendar_text
        idx: int = message.from_user.id
        if message.text is not None:
            calendar_text = message.text
            bot.send_message(idx, 'Подпись установлена')
        else:
            bot.send_message(idx, 'Что то пошло не так')
            raise MessageTextEmpty('Can\'t handle new calendar')

    @bot.message_handler(commands=['setintro'])
    def set_intro(message: Message):
        idx: int = message.from_user.id
        if idx in admins and message.chat.type == 'private':
            bot.send_message(idx, 'Введите новое приветствие')
            bot.register_next_step_handler_by_chat_id(idx, handle_new_intro)

    def handle_new_intro(message: Message):
        global intro
        if message.text is not None:
            intro = message.text
        else:
            raise MessageTextEmpty('Can\'t handle intro')

    @bot.message_handler(content_types=['new_chat_members'])
    def react_new_user(message: Message):
        idx: int = message.from_user.id
        bot.send_message(message.chat.id, intro)

    @bot.message_handler(commands=['welcome'])
    def welcome_message(message: Message):
        idx = bot.get_me().id
        button_welcome = InlineKeyboardButton(
            'Бот', callback_data='foo', url=f'tg://user?id={idx}')
        keyboard = InlineKeyboardMarkup()
        keyboard.add(button_welcome)
        bot.send_message(message.chat.id, text=welcome,
                         reply_markup=keyboard)

    @bot.message_handler(commands=['setwelcome'])
    def set_welcome(message: Message):
        idx: int = message.from_user.id
        if idx in admins and message.chat.type == 'private':
            bot.send_message(idx, 'Введите новое сообщение для закрепа')
            bot.register_next_step_handler_by_chat_id(idx, handle_new_welcome)

    def handle_new_welcome(message: Message):
        global welcome
        if message.text is not None:
            welcome = message.text
        else:
            raise MessageTextEmpty('Can\'t handle welcome')

    bot.polling()
    # bot = TelegramBot(TOKEN, ADMIN_ID, ADMIN_TINKOFF_TOKEN,
    #                   DELAY, logger, exception_handler)
    # bot.run()
