import logging
import json
import os
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked

API_TOKEN = os.getenv("BOT_TOKEN")  # переменная окружения

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Файл с базой пользователей
USER_DATA_FILE = 'user_data.json'

# Загружаем или создаём базу
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

# 15 способов заработка
methods = [
    "💼 Способ 1: Зарегистрируйся на сайте фриланса и предложи простые услуги: обработка текста, проверка орфографии...",
    "📷 Способ 2: Продавай свои фото на стоках – даже с телефона!",
    "📋 Способ 3: Делай резюме/портфолио за деньги (находи клиентов в Telegram/Avito)",
    "📢 Способ 4: Помогай малому бизнесу — введи Instagram, делай посты, сторис",
    "📝 Способ 5: Пиши тексты для блогов (можно с помощью ИИ)",
    "🎨 Способ 6: Создай обложки для видео/подкастов, продавай на фриланс-биржах",
    "📲 Способ 7: Делай Telegram-ботов под запрос (простые можно собрать без кода)",
    "🛒 Способ 8: Продавай товары по дропшиппингу — ищи поставщиков, продавай через Telegram",
    "🧠 Способ 9: Консультации по темам, где ты эксперт: учёба, психология, карьера",
    "🎮 Способ 10: Помоги детям или взрослым проходить уровни в играх",
    "💰 Способ 11: Смотри рекламу/задания в приложениях, получай кешбэк",
    "👀 Способ 12: Модерация комментариев в соцсетях",
    "🔎 Способ 13: Ресерч и подбор товаров/услуг на заказ",
    "📚 Способ 14: Делай подборки фильмов, книг и продавай как подборку",
    "🧩 Способ 15: Перепродавай обучающие материалы с ценностью (рефераты, шпоры, шаблоны)"
]

# Приветствие
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users.append(user_id)
        save_users(users)
    await message.answer(
        "Привет! Это 'Схемка прилетела' – твой ежедневный помощник по заработку онлайн.\n\n"
        "Готов(а) начать прямо сейчас?",
        reply_markup=start_keyboard()
    )

# Кнопка начать
def start_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Да, поехали!", callback_data='start_methods'))
    return kb

# Перелистывание схем
@dp.callback_query_handler(lambda c: c.data.startswith('start_methods') or c.data.startswith('method_'))
async def send_method(callback_query: types.CallbackQuery):
    if callback_query.data == 'start_methods':
        index = 0
    else:
        index = int(callback_query.data.split('_')[1])

    text = methods[index]

    kb = InlineKeyboardMarkup()
    if index > 0:
        kb.insert(InlineKeyboardButton("⬅️ Назад", callback_data=f'method_{index - 1}'))
    if index < len(methods) - 1:
        kb.insert(InlineKeyboardButton("Вперёд ➡️", callback_data=f'method_{index + 1}'))

    # Последняя кнопка — "Я всё посмотрел"
    kb.add(InlineKeyboardButton("✅ Я всё посмотрел", callback_data='done_reading'))

    await callback_query.message.edit_text(text, reply_markup=kb)

# После того как пользователь всё посмотрел
@dp.callback_query_handler(lambda c: c.data == 'done_reading')
async def finish_reading(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Отлично! Завтра прилетит новая схема. Заглядывай в бота в 12:00 🕛")

# Рассылка каждый день
async def daily_broadcast():
    now = datetime.now()
    while True:
        if datetime.now().hour == 12:
            for user_id in users:
                try:
                    await bot.send_message(user_id, f"📬 Новая схема дня!\n\n💡 {methods[datetime.now().day % len(methods)]}")
                except BotBlocked:
                    continue
            await asyncio.sleep(3600)  # Подождём 1 час, чтобы не дублировать
        else:
            await asyncio.sleep(300)  # Проверяем каждые 5 мин

# Запуск
if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(daily_broadcast())
    executor.start_polling(dp, skip_updates=True)
