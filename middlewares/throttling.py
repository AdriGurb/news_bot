from datetime import datetime, timedelta
from aiogram import types
from aiogram import BaseMiddleware
from collections import defaultdict

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, message_limit=3, time_window=5, ban_duration=150):
        self.message_limit = message_limit
        self.time_window = time_window
        self.ban_duration = ban_duration  # Длительность бана в секундах
        self.user_activity = defaultdict(dict)
        super().__init__()

    async def __call__(self, handler, event: types.Message, data: dict):
        current_user = event.from_user.id
        current_time = datetime.now()

        # Инициализация записи о пользователе
        if 'timestamps' not in self.user_activity[current_user]:
            self.user_activity[current_user]['timestamps'] = []
        
        # Проверка активного бана
        if current_user in self.user_activity and 'ban_expires' in self.user_activity[current_user]:
            if current_time < self.user_activity[current_user]['ban_expires']:
                return
            else:
                del self.user_activity[current_user]['ban_expires']

        # Фильтрация старых сообщений
        self.user_activity[current_user]['timestamps'] = [
            timestamp for timestamp in self.user_activity[current_user]['timestamps'] 
            if (current_time - timestamp).total_seconds() < self.time_window
        ]

        # Проверка превышения лимита
        if len(self.user_activity[current_user]['timestamps']) >= self.message_limit:
            self.user_activity[current_user]['ban_expires'] = current_time + timedelta(seconds=self.ban_duration)
            return

        # Добавление текущего сообщения
        self.user_activity[current_user]['timestamps'].append(current_time)
        
        return await handler(event, data)
