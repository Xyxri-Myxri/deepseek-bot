from aiogram import Router, types
from aiogram.filters import Command

from bot.keyboards.main import MAIN_MENU

router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот, который поможет тебе с ответами. Выбери действие:",
        reply_markup=MAIN_MENU,
    )


@router.message(lambda msg: msg.text == "⬅️ Назад в меню")
async def back_to_menu(message: types.Message):
    """Возвращает в главное меню"""
    await message.answer("🔙 Главное меню", reply_markup=MAIN_MENU)
