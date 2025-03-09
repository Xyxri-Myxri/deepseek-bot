import redis.asyncio as redis
import functools
from aiogram import types

from bot.config import RATE_LIMIT, REDIS_HOST, REDIS_PORT

# Подключение к Redis
redis_client = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), decode_responses=True)


async def is_rate_limited(user_id: int) -> bool:
    """Проверяет, превышен ли лимит запросов"""
    key = f"rate_limit:{user_id}"
    count = await redis_client.get(key)

    if count is None:
        # Первый запрос, создаем счетчик с TTL 60 секунд
        await redis_client.set(key, 1, ex=60)
        return False

    count = int(count)
    if count >= RATE_LIMIT:
        return True  # Лимит превышен

    # Увеличиваем счетчик
    await redis_client.incr(key)
    return False


def limit_requests():
    """Декоратор для ограничения запросов"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            if await is_rate_limited(message.from_user.id):
                await message.answer(
                    "🚫 *Вы превысили лимит запросов! Подождите минуту.*",
                    parse_mode="Markdown",
                )
                return
            return await func(message, *args, **kwargs)

        return wrapper

    return decorator
