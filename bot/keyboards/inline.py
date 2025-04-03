from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_history_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру для пагинации истории"""
    keyboard = []

    # Кнопки навигации
    if total_pages > 1:
        row = []
        if page > 1:
            row.append(
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"history_{page - 1}"
                )
            )
        if page < total_pages:
            row.append(
                InlineKeyboardButton(
                    text="Вперед ➡️", callback_data=f"history_{page + 1}"
                )
            )
        keyboard.append(row)

    # Кнопка закрытия
    keyboard.append(
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_history")]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_info_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для информации"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="📜 История запросов", callback_data="show_history"
            )
        ],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_info")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
