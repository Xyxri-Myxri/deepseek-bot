from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎨 Выбрать стиль ответа")],
        [
            KeyboardButton(text="📜 История запросов"),
            KeyboardButton(text="ℹ️ Информация"),
        ],
        [KeyboardButton(text="🔧 Настройки")],
    ],
    resize_keyboard=True,
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

# Клавиатура после выбора стиля
QUERY_KB = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад в меню")]],
    resize_keyboard=True,
)

# Настройки
SETTINGS_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔧 Query Enhancement")],
        [KeyboardButton(text="⬅️ Назад в меню")],
    ],
    resize_keyboard=True,
)

# Query Enhancement настройки
ENHANCEMENT_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Включить"), KeyboardButton(text="❌ Отключить")],
        [KeyboardButton(text="⬅️ Назад к настройкам")],
    ],
    resize_keyboard=True,
)
