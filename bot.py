import threading
import time
import logging
import json
import os
import random
import sqlite3

import telebot

from flask import Flask


TOKEN = "8969226485:AAHC9w8VxifEvIqraHCIcp4jm5ymwPlvDlw"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


CHARACTERS_FILE = "characters.json"
DB_FILE = "users.db"


@app.route("/")
def home():
    return "HoneyRealmBot is running!"


# ==========================
# Персонажи
# ==========================

try:
    with open(
        CHARACTERS_FILE,
        "r",
        encoding="utf-8-sig"
    ) as file:
        characters = json.load(file)

except Exception as e:
    logging.error(
        f"Ошибка загрузки персонажей: {e}"
    )
    characters = []


# ==========================
# SQLite
# ==========================

def db_connect():
    return sqlite3.connect(DB_FILE)


def init_db():

    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS collections (
            user_id TEXT,
            character TEXT,
            UNIQUE(user_id, character)
        )
        """
    )

    conn.commit()
    conn.close()


init_db()


def get_collection(user_id):

    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT character FROM collections WHERE user_id=?",
        (str(user_id),)
    )

    result = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return result


def add_character(user_id, character):

    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO collections
        (user_id, character)
        VALUES (?, ?)
        """,
        (
            str(user_id),
            character
        )
    )

    conn.commit()
    conn.close()



# ==========================
# Получение персонажа
# ==========================

def get_character(user_id):

    collected = get_collection(user_id)


    available = [

        c for c in characters

        if c["name"] not in collected

    ]


    total = len(characters)
    owned = len(collected)


    if available:

        progress = owned / total if total else 1


        if progress < 0.5:
            chance = 90

        elif progress < 0.8:
            chance = 70

        elif progress < 1:
            chance = 40

        else:
            chance = 10


        if random.randint(1,100) <= chance:

            character = random.choice(
                available
            )

            add_character(
                user_id,
                character["name"]
            )

            return character


    return random.choice(characters)



# ==========================
# Отправка
# ==========================

def send_character(message):

    character = get_character(
        message.from_user.id
    )


    image_path = os.path.join(
        os.getcwd(),
        character["image"]
    )


    caption = (

        f"🍯 <b>{character['name']}</b>\n\n"

        f"<i>{character['description']}</i>\n\n"

        "📖 Персонаж получен!"

    )


    if not os.path.exists(image_path):

        bot.send_message(
            message.chat.id,
            "⚠️ Картинка персонажа не найдена."
        )

        return


    try:

        with open(
            image_path,
            "rb"
        ) as photo:

            bot.send_photo(

                message.chat.id,

                photo,

                caption=caption,

                parse_mode="HTML"

            )


    except Exception as e:

        logging.error(
            f"Ошибка отправки фото: {e}"
        )



# ==========================
# Команды
# ==========================

@bot.message_handler(
    commands=["start"]
)

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

        "🍯 Добро пожаловать в HoneyRealm!\n\n"
        "Собирай уникальных персонажей.",

        reply_markup=markup

    )



@bot.message_handler(
    func=lambda message:
    message.text == "🍯 Узнать, кто я"
)

def button_character(message):

    send_character(message)



@bot.message_handler(
    commands=["honey"]
)

def honey(message):

    send_character(message)



@bot.message_handler(
    commands=["collection"]
)

def collection(message):

    collected = get_collection(
        message.from_user.id
    )


    text = (

        "🍯 <b>Твоя коллекция HoneyRealm</b>\n\n"

        f"Открыто: {len(collected)}/{len(characters)}\n\n"

    )


    if collected:

        for i, name in enumerate(
            collected,
            start=1
        ):

            text += f"{i}. {name}\n"


    else:

        text += "Коллекция пуста."


    bot.send_message(

        message.chat.id,

        text,

        parse_mode="HTML"

    )



@bot.message_handler(
    commands=["stats"]
)

def stats(message):

    count = len(
        get_collection(
            message.from_user.id
        )
    )


    bot.send_message(

        message.chat.id,

        "🍯 <b>Статистика</b>\n\n"
        f"Получено персонажей: {count}",

        parse_mode="HTML"

    )



@bot.message_handler(
    commands=["help"]
)

def help_command(message):

    bot.send_message(

        message.chat.id,

        "🍯 <b>HoneyRealmBot</b>\n\n"
        "/honey — получить персонажа\n"
        "/collection — коллекция\n"
        "/stats — статистика\n"
        "/help — помощь",

        parse_mode="HTML"

    )



# ==========================
# Flask
# ==========================

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



threading.Thread(
    target=run_flask,
    daemon=True
).start()



logging.info(
    "HoneyRealmBot запущен"
)



while True:

    try:

        bot.infinity_polling(

            skip_pending=True,

            timeout=30,

            long_polling_timeout=30

        )


    except Exception as e:

        logging.error(
            f"Polling ошибка: {e}"
        )

        time.sleep(10)
