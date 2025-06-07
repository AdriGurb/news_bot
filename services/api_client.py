import time
import aiohttp
from aiohttp import ClientError, ClientTimeout

class Client:
    def __init__(self, api_key_news: str, cache_ttl: int = 600, timeout: int = 10):
        self.api_key_wheater = api_key_news
        self.base_url = "https://newsapi.org/v2/"
        self.timeout = timeout  # Таймаут запроса в секундах

        self._wheater_cache: dict[str, tuple[float, dict]] = {}  # news -> (timestamp, data)
        self.cache_ttl = cache_ttl  # Время жизни кэша в секундах

    async def get_random_news(self, news: str) -> dict:
        now = time.time()

        # Проверка кэша
        if news in self._wheater_cache:
            ts, data = self._wheater_cache[news]
            if now - ts < self.cache_ttl:
                return data

        try:
            # Создаем клиент с таймаутом
            timeout = ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    async with session.get(
                        f"{self.base_url}/everything?q={news}&sortBy=publishedAt&language=ru&apiKey={self.api_key_wheater}"
                    ) as response:
                        data = await response.json()
                        
                        # Сохраняем в кэш
                        self._wheater_cache[news] = (now, data)
                        return data
                        
                except ClientError as e:
                    # Обработка ошибок соединения/таймаута
                    raise Exception(f"Failed to get weather data: {str(e)}")
                    
        except Exception as e:
            # Обработка других исключений
            raise Exception(f"Unexpected error occurred: {str(e)}")
