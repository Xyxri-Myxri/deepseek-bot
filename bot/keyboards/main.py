from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎨 Выбрать стиль ответа")]], resize_keyboard=True
)

# Выбор стиля ответа
STYLE_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣ Обычный"), KeyboardButton(text="2️⃣ Научный")],
        [KeyboardButton(text="3️⃣ С юмором"), KeyboardButton(text="4️⃣ Простым языком")],
        [
            KeyboardButton(text="5️⃣ Развернутый ответ"),
            KeyboardButton(text="⬅️ Назад в меню"),
        ],
    ],
    resize_keyboard=True,
)
