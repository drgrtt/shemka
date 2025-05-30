import json
import os
from aiogram import Bot, Dispatcher, executor, types

TOKEN = "8044456789:AAHZfhB5E16coRP__7lmj5dBQazyh-4N7K8"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

DATA_FILE = 'user_data.json'

earn_methods = [
    "1. Продажа товаров на маркетплейсах",
    "2. Фриланс: копирайтинг, дизайн",
    "3. Партнёрские программы",
    "4. Создание курсов и вебинаров",
    "5. Инвестиции в акции",
    "6. Блогинг и реклама",
    "7. Торговля на бирже",
    "8. Арбитраж трафика",
    "9. Ведение соцсетей для бизнеса",
    "10. Программирование и разработка",
    "11. Создание YouTube канала",
    "12. Продажа фото и видео",
    "13. Онлайн консультации",
    "14. Разработка мобильных приложений",
    "15. Дропшиппинг"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id

    data = load_data()
    users = data.get('users', [])
    if user_id not in users:
        users.append(user_id)
    data['users'] = users
    save_data(data)

    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Я готов, отправляй скорее!", callback_data="ready")
    keyboard.add(button)

    await message.answer(
        "Привет! Это *Схемка прилетела* — твой помощник по заработку.\n\n"
        "Ты готов? Нажми кнопку ниже, и я пришлю первые способы!",
        parse_mode='Markdown',
        reply_markup=keyboard
    )

def get_keyboard(page):
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    if page < len(earn_methods) - 1:
        nav_buttons.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data=f"page_{page+1}"))

    if nav_buttons:
        keyboard.row(*nav_buttons)  # Ряд с кнопками Назад и Вперёд

    # Отдельный ряд с кнопкой "Я всё посмотрел"
    keyboard.add(types.InlineKeyboardButton("Я всё посмотрел", callback_data="all_done"))

    return keyboard

async def send_earn_method(chat_id, page):
    text = earn_methods[page]
    await bot.send_message(chat_id, text, reply_markup=get_keyboard(page))

@dp.callback_query_handler(lambda c: c.data == "ready")
async def process_ready(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_earn_method(callback_query.message.chat.id, 0)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('page_'))
async def process_page(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=earn_methods[page],
        reply_markup=get_keyboard(page)
    )

@dp.callback_query_handler(lambda c: c.data == 'all_done')
async def all_done(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.message.chat.id,
        "Отлично! Каждый день будет новая порция способов заработка. Следи за обновлениями!"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
