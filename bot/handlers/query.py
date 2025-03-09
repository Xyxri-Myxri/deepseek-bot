from aiogram import Router, types, F
from aiogram.filters import Command

from bot.db.database import get_user_history, save_user_query
from bot.keyboards.main import STYLE_KB
from bot.services.deepseek import query_deepseek
from bot.utils.rate_limit import limit_requests

router = Router()

PRESET_OPTIONS = {
    "1️⃣ Обычный": "default",
    "2️⃣ Научный": "scientific",
    "3️⃣ С юмором": "humor",
    "4️⃣ Простым языком": "simple",
    "5️⃣ Развернутый ответ": "detailed",
}


@router.message(Command("history"))
async def user_history(message: types.Message):
    """Отправляет историю последних запросов"""
    user_id = message.from_user.id
    history = await get_user_history(user_id)

    if not history:
        await message.answer("📜 История пуста.", parse_mode="Markdown")
        return

    history_text = "\n\n".join(
        [
            f"🔹 Запрос: {item['query']}\n📝 Ответ: {item['response']}"
            for item in history
        ]
    )
    await message.answer(
        f"📌 Последние запросы:\n\n{history_text}", parse_mode="Markdown"
    )


@router.message(lambda msg: msg.text == "🎨 Выбрать стиль ответа")
async def choose_style(message: types.Message):
    """Выбор стиля ответа"""
    await message.answer("Выберите стиль ответа:", reply_markup=STYLE_KB)


@router.message(lambda msg: msg.text in PRESET_OPTIONS)
async def set_preset(message: types.Message):
    """Сохраняет выбранный стиль"""
    preset_name = PRESET_OPTIONS[message.text]
    await message.answer(
        f'✅ Стиль "{message.text}" установлен! Теперь отправьте свой запрос.'
    )
    message.bot.user_data[message.from_user.id] = preset_name  # Запоминаем стиль


@router.message(~F.text.startswith("/"))  # Не ловим команды
@limit_requests()
async def handle_query(message: types.Message):
    """Обрабатывает запрос с анимацией 'Обработка...' и форматированием"""
    user_id = message.from_user.id
    preset_name = message.bot.user_data.get(user_id, "default")  # Получаем стиль
    query_text = message.text.strip()

    # Отправляем временное сообщение
    response_msg = await message.answer(
        "⏳ *Обработка запроса...*", parse_mode="Markdown"
    )

    # Генерируем ответ
    response = await query_deepseek(message.text, preset_name)

    # Сохраняем в БД
    await save_user_query(user_id, query_text, response)

    # Редактируем сообщение с ответом
    await response_msg.edit_text(response, parse_mode="Markdown")
