from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import F
from services.api_client import Client
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.settings_news import news_config
from datetime import datetime
from random import randint

router = Router()

mal_client = Client(news_config.api_key_news)


# Использование: /news <news>
@router.message(Command("news"))
async def cmd_news(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Нужно написать название номер новости: /news видеокарты")

    news = parts[1].strip()
    await send_news(news, message)
    

# Выбрать по кнопке
@router.callback_query(lambda c: c.data.startswith("nexst_news_"))
async def cmd_change_city(query: CallbackQuery):
    meta_data = query.data.split("_", 2)[2].split(sep=",")
    news, num_news = meta_data[0], int(meta_data[1])#* не работает
    await send_news(news, query.message, num_news)


async def send_news(news, message: Message, num_news : int = 0):
    response = await mal_client.get_random_news(news)
    if response["status"] == "ok":
        try:
            response = response["articles"][num_news]
            text = f"{response['title']}\n\n{response['description']}\nСсылка: {response['url']}"
            kb = InlineKeyboardBuilder()
            kb.button(text=f">>>", callback_data=f"nexst_news_{news},{num_news+1}")
            kb.adjust(1)
            await message.reply(text, reply_markup=kb.as_markup())
        except:
            await message.reply("Нет новостей")
    else:
        return await message.reply(f"Произошла ошибка.\n Статус: {response['status']}\nКод: {response['codr']}\n сообщение api: {response['message']}")
    
