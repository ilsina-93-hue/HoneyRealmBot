import telebot
import json
import random
import os
import threading
import time
import logging
from flask import Flask

TOKEN = "8969226485:AAE7r92E1iz0hRn0zK9pRURTqkwyPgzeBeo"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ==========================================
# Flask
# ==========================================

@app.route("/")
def home():
    return "HoneyRealmBot is running!"


# ==========================================
# Загрузка персонажей
# ==========================================

CHARACTERS_FILE = "characters.json"

with open(
    CHARACTERS_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    characters = json.load(file)


# ==========================================
# Запоминание последних персонажей
# ==========================================

last_character = {}

HISTORY_LIMIT = 10

history = {}


# ==========================================
# Получить случайного персонажа
# ==========================================

def get_random_character(chat_id):

    if chat_id not in history:
        history[chat_id] = []

    available = [
        c for c in characters
        if c["name"] not in history[chat_id]
    ]

    if len(available) == 0:

        history[chat_id] = []

        available = characters.copy()

    character = random.choice(available)

    history[chat_id].append(
        character["name"]
    )

    if len(history[chat_id]) > HISTORY_LIMIT:
        history[chat_id].pop(0)

    return character


# ==========================================
# Отправка персонажа
# ==========================================

def send_character(chat_id):

    character = get_random_character(chat_id)

    image_name = character["image"]

    image_path = os.path.join(
        os.getcwd(),
        image_name
    )

    caption = (
        f"🍯 <b>{character['name']}</b>\n\n"
        f"<i>{character['description']}</i>"
    )

    logging.info(
        f"Выбран персонаж: {character['name']}"
    )

    if not os.path.exists(image_path):

        logging.error(
            f"Файл отсутствует: {image_name}"
        )

        bot.send_message(
            chat_id,
            "⚠️ Изображение персонажа не найдено."
        )

        return

    for attempt in range(3):

        try:

            with open(
                image_path,
                "rb"
            ) as photo:

                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption,
                    parse_mode="HTML",
                    timeout=60
                )

            logging.info(
                "Фото успешно отправлено."
            )

            return

        except Exception as e:

            logging.error(
                f"Ошибка отправки ({attempt+1}): {e}"
            )

            time.sleep(2)

    bot.send_message(
        chat_id,
        "⚠️ Не удалось отправить персонажа."
    )


# ==========================================
# /start
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.add(
        telebot.types.KeyboardButton(
            "🍯 Узнать, кто я"
        )
    )

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в HoneyRealm 🍯\n\n"
        "Нажмите кнопку ниже, чтобы узнать своего персонажа.",
        reply_markup=markup
    )


# ==========================================
# Кнопка
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "🍯 Узнать, кто я"
)
def button_handler(message):

    send_character(
        message.chat.id
    )
```
# ==========================================
# Команда /honey
# ==========================================

@bot.message_handler(
    commands=["honey"]
)
def honey(message):

    send_character(
        message.chat.id
    )


# ==========================================
# Команда /help
# ==========================================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    bot.send_message(

        message.chat.id,

        "🍯 <b>HoneyRealmBot</b>\n\n"

        "Доступные команды:\n\n"

        "/start — открыть меню\n"
        "/honey — получить случайного персонажа\n"
        "/help — помощь",

        parse_mode="HTML"

    )


# ==========================================
# Inline режим
# ==========================================

@bot.inline_handler(
    func=lambda query: True
)
def inline_help(query):

    result = telebot.types.InlineQueryResultArticle(

        id="honeyrealm",

        title="🍯 HoneyRealmBot",

        description="Получить персонажа HoneyRealm",

        input_message_content=
        telebot.types.InputTextMessageContent(

            message_text=

            "🍯 <b>HoneyRealmBot</b>\n\n"

            "Чтобы получить своего персонажа:\n\n"

            "• откройте личный чат с ботом\n"
            "• нажмите кнопку «🍯 Узнать, кто я»\n\n"

            "или\n\n"

            "используйте команду\n"
            "/honey",

            parse_mode="HTML"

        )

    )

    try:

        bot.answer_inline_query(

            query.id,

            [result],

            cache_time=0,

            is_personal=True

        )

    except Exception as e:

        logging.error(

            f"Inline error: {e}"

        )


# ==========================================
# Неизвестные команды
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text is not None
    and message.text.startswith("/")
)
def unknown_command(message):

    bot.send_message(

        message.chat.id,

        "❌ Такой команды не существует.\n\n"
        "Используйте /help."

    )


# ==========================================
# Flask
# ==========================================

def run_flask():

    port = int(

        os.environ.get(

            "PORT",

            10000

        )

    )

    app.run(

        host="0.0.0.0",

        port=port

    )


# ==========================================
# Запуск Flask
# ==========================================

threading.Thread(

    target=run_flask,

    daemon=True

).start()


logging.info(

    "HoneyRealmBot запущен."

)


# ==========================================
# Polling
# ==========================================

while True:

    try:

        logging.info(

            "Запуск polling..."

        )

        bot.infinity_polling(

            skip_pending=True,

            timeout=30,

            long_polling_timeout=30

        )

    except Exception as e:

        logging.error(

            f"Polling crashed: {e}"

        )

        time.sleep(10)
