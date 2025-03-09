from aiogram import Router, types
from bot.services.deepseek import query_deepseek

router = Router()

@router.message()
async def handle_query(message: types.Message):
    user_query = message.text.strip()
    if not user_query:
        await message.answer("Введите корректный запрос.")
        return

    await message.answer("Обрабатываю запрос...")

    response = await query_deepseek(user_query)
    
    await message.answer(response)
