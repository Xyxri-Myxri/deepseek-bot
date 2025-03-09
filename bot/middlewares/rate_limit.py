from aiogram.types import Message
from aiogram import BaseMiddleware
import asyncio

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit: int):
        self.limit = limit
        self.users = {}

    async def __call__(self, handler, message: Message, data):
        user_id = message.from_user.id
        if user_id in self.users and self.users[user_id] >= self.limit:
            await message.answer("Превышен лимит запросов. Попробуйте позже.")
            return
        
        self.users[user_id] = self.users.get(user_id, 0) + 1
        # await asyncio.sleep(60)
        self.users[user_id] -= 1

        return await handler(message, data)
