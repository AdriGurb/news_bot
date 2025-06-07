from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import logging
from keyboards.builders import keyboard


router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Хай! Я бот для поиска новостей\n"
                         "Введи /help для вывода списка доступных команд",
                         reply_markup=keyboard)

    logging.info(f"User {message.from_user.id} called /start")

@router.message(Command("help"))
async def help(message: Message):
    await message.answer(
        "Команды:\n"
        "/start - приветсвие\n"
        "/news новость - найти новость\n"
        "/favs - показать избранные новости\n"
        "/add новость - добавить в избранное\n"
        "/del новость - удалить из избранного\n"
        "/help- все команды\n"
        "/support- поддержка"
    )
