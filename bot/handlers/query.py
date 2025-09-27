import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.db.database import get_user_history, save_user_query
from bot.keyboards.main import STYLE_KB, QUERY_KB, MAIN_MENU, SETTINGS_KB, ENHANCEMENT_KB
from bot.keyboards.inline import get_history_keyboard, get_info_keyboard
from bot.services.deepseek import query_deepseek
from bot.services.query_enhancement import enhance_query, should_enhance_query, get_query_analysis
from bot.utils.rate_limit import limit_requests

router = Router()

PRESET_OPTIONS = {
    "1️⃣ Обычный": "default",
    "2️⃣ Научный": "scientific",
    "3️⃣ С юмором": "humor",
    "4️⃣ Простым языком": "simple",
    "5️⃣ Развернутый ответ": "detailed",
}

# Константы для пагинации
HISTORY_PER_PAGE = 3
MAX_MESSAGE_LENGTH = 4000


async def format_history_message(history: list, page: int) -> tuple[str, int]:
    """Форматирует сообщение с историей запросов"""
    start_idx = (page - 1) * HISTORY_PER_PAGE
    end_idx = start_idx + HISTORY_PER_PAGE
    page_history = history[start_idx:end_idx]

    message_parts = []
    for item in page_history:
        query = (
            item["query"][:100] + "..." if len(item["query"]) > 100 else item["query"]
        )
        response = (
            item["response"][:200] + "..."
            if len(item["response"]) > 200
            else item["response"]
        )
        message_parts.append(f"🔹 Запрос: {query}\n📝 Ответ: {response}\n")

    total_pages = (len(history) + HISTORY_PER_PAGE - 1) // HISTORY_PER_PAGE
    message = f"📌 История запросов (страница {page}/{total_pages}):\n\n" + "\n".join(
        message_parts
    )

    # Если сообщение слишком длинное, обрезаем его
    if len(message) > MAX_MESSAGE_LENGTH:
        message = message[:MAX_MESSAGE_LENGTH] + "..."

    return message, total_pages


@router.message(Command("history"))
@router.message(lambda msg: msg.text == "📜 История запросов")
async def user_history(message: types.Message):
    """Отправляет историю последних запросов"""
    user_id = message.from_user.id
    history = await get_user_history(
        user_id, limit=100
    )  # Получаем больше записей для пагинации

    if not history:
        await message.answer("📜 История пуста.", parse_mode="Markdown")
        return

    message_text, total_pages = await format_history_message(history, 1)
    keyboard = get_history_keyboard(1, total_pages)
    await message.answer(message_text, parse_mode="Markdown", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("history_"))
async def process_history_pagination(callback_query: types.CallbackQuery):
    """Обрабатывает пагинацию истории"""
    page = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    history = await get_user_history(user_id, limit=100)

    message_text, total_pages = await format_history_message(history, page)
    keyboard = get_history_keyboard(page, total_pages)

    await callback_query.message.edit_text(
        message_text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "close_history")
async def close_history(callback_query: types.CallbackQuery):
    """Закрывает историю запросов"""
    await callback_query.message.delete()
    await callback_query.answer()


@router.message(lambda msg: msg.text == "ℹ️ Информация")
async def show_info(message: types.Message):
    """Показывает информацию о боте и командах"""
    info_text = """
🤖 *Информация о боте*

*Основные команды:*
• Отправьте любой текст - бот ответит на ваш запрос
• /history или кнопка "📜 История запросов" - просмотр истории запросов
• "🎨 Выбрать стиль ответа" - выбор стиля ответа

*Стили ответа:*
1️⃣ Обычный - стандартный ответ
2️⃣ Научный - ответ с научной точки зрения
3️⃣ С юмором - ответ с элементами юмора
4️⃣ Простым языком - упрощенный ответ
5️⃣ Развернутый ответ - подробный ответ

*Ограничения:*
• Rate limiting: ограничение на количество запросов в минуту
• Максимальная длина сообщения: 4000 символов
"""
    await message.answer(
        info_text, parse_mode="Markdown", reply_markup=get_info_keyboard()
    )


@router.callback_query(lambda c: c.data == "close_info")
async def close_info(callback_query: types.CallbackQuery):
    """Закрывает информацию"""
    await callback_query.message.delete()
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "show_history")
async def show_history_from_info(callback_query: types.CallbackQuery):
    """Показывает историю из информационного меню"""
    await callback_query.message.delete()
    await user_history(callback_query.message)
    await callback_query.answer()


@router.message(lambda msg: msg.text == "🎨 Выбрать стиль ответа")
async def choose_style(message: types.Message):
    """Выбор стиля ответа"""
    await message.answer("Выберите стиль ответа:", reply_markup=STYLE_KB)


@router.message(lambda msg: msg.text in PRESET_OPTIONS)
async def set_preset(message: types.Message):
    """Сохраняет выбранный стиль"""
    user_id = message.from_user.id
    preset_name = PRESET_OPTIONS[message.text]
    current_preset = message.bot.user_data.get(user_id, "default")
    
    if current_preset == preset_name:
        await message.answer(
            f'ℹ️ Стиль "{message.text}" уже выбран!',
            reply_markup=QUERY_KB,
        )
        return
        
    message.bot.user_data[user_id] = preset_name  # Запоминаем стиль
    await message.answer(
        f'✅ Стиль "{message.text}" установлен!\n\nТеперь отправьте свой запрос',
        reply_markup=QUERY_KB,
    )


@router.message(lambda msg: msg.text == "❌ Отменить ввод")
async def cancel_query(message: types.Message):
    """Отменяет ввод запроса и возвращает в главное меню"""
    if message.from_user.id in message.bot.user_data:
        del message.bot.user_data[message.from_user.id]
    await message.answer("❌ Ввод запроса отменен", reply_markup=MAIN_MENU)


@router.message(lambda msg: msg.text == "⬅️ Назад в меню")
async def back_to_menu(message: types.Message):
    """Возвращает в главное меню"""
    if message.from_user.id in message.bot.user_data:
        del message.bot.user_data[message.from_user.id]
    await message.answer("🔙 Главное меню", reply_markup=MAIN_MENU)


@router.message(lambda msg: msg.text == "🔧 Настройки")
async def show_settings(message: types.Message):
    """Показывает настройки бота"""
    await message.answer("⚙️ Настройки бота:", reply_markup=SETTINGS_KB)


@router.message(lambda msg: msg.text == "🔧 Query Enhancement")
async def show_enhancement_settings(message: types.Message):
    """Показывает настройки Query Enhancement"""
    user_id = message.from_user.id
    enhancement_enabled = message.bot.user_data.get(f"{user_id}_enhancement", True)
    
    status = "✅ Включено" if enhancement_enabled else "❌ Отключено"
    await message.answer(
        f"🔧 *Query Enhancement*\n\n"
        f"Текущий статус: {status}\n\n"
        f"Query Enhancement автоматически улучшает ваши запросы для получения более качественных ответов.",
        parse_mode="Markdown",
        reply_markup=ENHANCEMENT_KB
    )


@router.message(lambda msg: msg.text == "✅ Включить")
async def enable_enhancement(message: types.Message):
    """Включает Query Enhancement"""
    user_id = message.from_user.id
    message.bot.user_data[f"{user_id}_enhancement"] = True
    await message.answer(
        "✅ Query Enhancement включен!\n\nТеперь ваши запросы будут автоматически улучшаться для лучших ответов.",
        reply_markup=SETTINGS_KB
    )


@router.message(lambda msg: msg.text == "❌ Отключить")
async def disable_enhancement(message: types.Message):
    """Отключает Query Enhancement"""
    user_id = message.from_user.id
    message.bot.user_data[f"{user_id}_enhancement"] = False
    await message.answer(
        "❌ Query Enhancement отключен!\n\nЗапросы будут обрабатываться без улучшений.",
        reply_markup=SETTINGS_KB
    )


@router.message(lambda msg: msg.text == "⬅️ Назад к настройкам")
async def back_to_settings(message: types.Message):
    """Возвращает к настройкам"""
    await show_settings(message)


@router.message(~F.text.startswith("/"))  # Не ловим команды
@limit_requests()
async def handle_query(message: types.Message):
    """Обрабатывает запрос с Query Enhancement и анимацией 'Обработка...'"""
    user_id = message.from_user.id
    preset_name = message.bot.user_data.get(user_id, "default")  # Получаем стиль
    original_query = message.text.strip()

    # Отправляем временное сообщение
    response_msg = await message.answer(
        "⏳ *Обработка запроса...*", parse_mode="Markdown"
    )

    # Query Enhancement: проверяем настройки пользователя и улучшаем запрос
    enhanced_query = original_query
    enhancement_used = False
    enhancement_enabled = message.bot.user_data.get(f"{user_id}_enhancement", True)
    
    # Логируем оригинальный запрос
    logging.info(f"User {user_id} original query: '{original_query}'")
    
    if enhancement_enabled and await should_enhance_query(original_query):
        enhanced_query = await enhance_query(original_query)
        if enhanced_query != original_query:
            enhancement_used = True
            # Логируем улучшенный запрос
            logging.info(f"User {user_id} enhanced query: '{enhanced_query}'")
            # Обновляем сообщение о том, что запрос улучшен
            await response_msg.edit_text(
                "🔧 *Улучшаю запрос для лучшего ответа...*", parse_mode="Markdown"
            )
        else:
            logging.info(f"User {user_id} query enhancement: no improvement needed")
    else:
        logging.info(f"User {user_id} query enhancement: disabled or not needed")

    # Генерируем ответ с улучшенным запросом
    response = await query_deepseek(enhanced_query, preset_name)

    # Добавляем информацию об улучшении в ответ (опционально)
    if enhancement_used and len(enhanced_query) > len(original_query):
        response = f"💡 *Улучшенный запрос:* {enhanced_query}\n\n" + response

    # Сохраняем в БД (сохраняем оригинальный запрос и улучшенный)
    await save_user_query(user_id, original_query, response)

    # Редактируем сообщение с ответом
    await response_msg.edit_text(response, parse_mode="Markdown")

    # Очищаем выбранный стиль
    if user_id in message.bot.user_data:
        del message.bot.user_data[user_id]
