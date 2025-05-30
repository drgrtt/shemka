import logging
import os
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8044456789:AAHZfhB5E16coRP__7lmj5dBQazyh-4N7K8"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

WAYS = [
    "💼 Способ 1: Продажа дизайнов на Canva — сделай шаблон, выложи на Etsy, получай $$$",
    "📱 Способ 2: Рефералки на сервисы — делай обзор, кидай ссылку и получай %",
    # ... добавь остальные способы здесь ...
    "🌍 Способ 15: Переводи популярные схемы с англ. TikTok на русский"
]

PARTNER_CHANNELS = [
    {"name": "Канал 1", "link": "https://t.me/channel1"},
    {"name": "Канал 2", "link": "https://t.me/channel2"},
]

DATA_FILE = "user_data.json"

def load_user_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_pages = load_user_data()

def get_page_markup(page):
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("← Назад", callback_data=f"page_{page - 1}"))
    if page < len(WAYS) - 1:
        buttons.append(InlineKeyboardButton("Вперёд →", callback_data=f"page_{page + 1}"))
    else:
        buttons.append(InlineKeyboardButton("✅ Я всё посмотрел, а что ещё?", callback_data="finished"))
    return InlineKeyboardMarkup().add(*buttons)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    chat_id = str(message.chat.id)
    if chat_id not in user_pages:
        user_pages[chat_id] = 0
        save_user_data(user_pages)
    await message.answer("Привет! Готов(а) получать схемки для заработка?")
    await send_page(chat_id, user_pages[chat_id])

async def send_page(chat_id, page):
    user_pages[str(chat_id)] = page
    save_user_data(user_pages)
    text = f"{WAYS[page]}"
    markup = get_page_markup(page)
    await bot.send_message(chat_id, text, reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def change_page(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[1])
    chat_id = str(callback_query.message.chat.id)
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await send_page(chat_id, page)

@dp.callback_query_handler(lambda c: c.data == "finished")
async def finished_view(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    channels_text = "📢 Сначала подпишись на каналы наших друзей:\n"
    for ch in PARTNER_CHANNELS:
        channels_text += f"- [{ch['name']}]({ch['link']})\n"
    await bot.send_message(callback_query.message.chat.id,
        "🔥 Завтра будет ещё новая порция способов!\n\n" + channels_text,
        parse_mode="Markdown"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
