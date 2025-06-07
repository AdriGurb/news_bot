from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from states.support_states import SupportStates
from filters.filters import IsAdmin, IsSupport
from config.settings_admins import admins_config
from config.settings_bot import bot_config

# Список администраторов
admin_list = admins_config.settings_admins

#Инициализируем бота и роутер
telegram_bot = Bot(token=bot_config.telegram_api_key)
support_router = Router()

# Обработчик команды поддержки
@support_router.message(F.text == "/support")
async def handle_support_request(message: types.Message, state: FSMContext):
    await state.set_state(SupportStates.waiting_for_question)
    await message.answer("Опишите проблему максимально подробно.")

# Обработчик вопроса пользователя
@support_router.message(SupportStates.waiting_for_question)
async def handle_user_question(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text, user_id=message.from_user.id)
    
    # Формируем клавиатуру для админов
    reply_keyboard = InlineKeyboardBuilder()
    reply_keyboard.button(text="Ответить", callback_data=f"reply_{message.from_user.id}")
    
    # Рассылка вопроса админам
    for admin in admin_list:
        try:
            await telegram_bot.send_message(
                chat_id=admin,
                text=f"Support ticket from {message.from_user.full_name} (ID: {message.from_user.id}):\n\n"
                     f"{message.text}",
                reply_markup=reply_keyboard.as_markup()
            )
        except Exception as error:
            print(f"Ошибка отправки админу {admin}: {error}")
    
    await message.answer("Вопрос отправлен в поддержку.")
    await state.clear()

# Обработчик ответа админа через reply
@support_router.message(IsAdmin(), IsSupport())
async def handle_admin_reply(message: types.Message):
    replied_message = message.reply_to_message.text
    recipient_id = int(replied_message.split("ID: ")[1].split(")")[0])
    
    await telegram_bot.send_message(
        recipient_id,
        f"Ответ поддержки:\n\n{message.text}"
    )
    
    await message.answer("Ответ отправлен.")

# Обработчик кнопки ответа
@support_router.callback_query(F.data.startswith("reply_"))
async def handle_reply_button(callback: types.CallbackQuery, state: FSMContext):
    recipient = int(callback.data.split("_")[1])
    await state.update_data(target_user_id=recipient)
    await state.set_state(SupportStates.waiting_for_response)
    await callback.message.answer(f"Ответе пользователю {recipient}:")
    await callback.answer()

# Обработчик ответа админа через состояние
@support_router.message(SupportStates.waiting_for_response)
async def process_admin_reply(message: types.Message, state: FSMContext):
    context_data = await state.get_data()
    recipient = context_data['target_user_id']
    
    await telegram_bot.send_message(
        recipient,
        f"Ответ поддержки:\n\n{message.text}"
    )
    
    await message.answer("Ваш ответ был отправлен пользователю.")
    await state.clear()
