import asyncpg

from bot.config import (
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

# Подключение к базе данных
DB_PARAMS = {
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "database": POSTGRES_DB,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
}


async def init_db():
    """Создает пул подключений к БД"""
    return await asyncpg.create_pool(**DB_PARAMS)


async def save_user_query(user_id: int, query: str, response: str):
    """Сохраняет запрос пользователя в БД"""
    pool = await init_db()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO history (user_id, query, response) VALUES ($1, $2, $3)",
            user_id,
            query,
            response,
        )


async def get_user_history(user_id: int, limit: int = 5):
    """Получает последние запросы пользователя"""
    pool = await init_db()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT query, response, timestamp FROM history WHERE user_id = $1 ORDER BY timestamp DESC LIMIT $2",
            user_id,
            limit,
        )
    return rows
