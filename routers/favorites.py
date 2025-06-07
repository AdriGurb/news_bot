from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from services.favorites_storage import FavoritesStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from routers.news import send_news

router = Router()

# инициализируем хранилище (файл рядом с bot.py: storage/favorites.json)
storage = FavoritesStorage("storage/favorites.json")

# ---- Добавить в избранное ----
# Использование: /add <news>
@router.message(Command("add"))
async def cmd_add_fav(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Нужно написать новость: /add рынок акций")

    city = parts[1].strip()
    # опционально можно проверить существование через mal_client.anime_exists
    await storage.add(message.from_user.id, city)
    await message.reply(f"Город {city} добавлен в избранное.")

# ---- Список избранного ----
@router.message(Command("favs"))
async def cmd_list_fav(message: Message):
    favs = await storage.list(message.from_user.id)
    if not favs:
        return await message.reply("Нет избранного 🙁")
    text = "Избранное:\n" + "\n".join(f"- {a}" for a in favs)
    # кнопки для выбора каждого:
    kb = InlineKeyboardBuilder()
    for fav in favs:
        kb.button(text=f"{fav}", callback_data=f"send_news_{fav}")
    kb.adjust(1)
    await message.reply(text, reply_markup=kb.as_markup())

# Выбрать по кнопке
@router.callback_query(lambda c: c.data.startswith("send_news_"))
async def cmd_send_news(query: CallbackQuery):
    fav = query.data.split("_", 2)[2]
    await send_news(fav, query.message)

# ---- Удалить из избранного командой ----
@router.message(Command("del"))
async def cmd_remove_fav(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply("Нужно написать новость: /add рынок акций")
    fsv = parts[1].strip()
    await storage.remove(message.from_user.id, fav)
    await message.reply(f"❌ {fav} удален из избранного.")



