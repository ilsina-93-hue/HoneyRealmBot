import threading
import time
import logging
import json
import os
import random

import telebot

from flask import Flask


TOKEN = "8969226485:AAFL-Vwi58aU0PlPyvkgpgHGKhBXGj4aDA8"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


CHARACTERS_FILE = "characters.json"
USERS_FILE = "users.json"
BACKUP_FILE = "users_backup.json"



@app.route("/")
def home():
    return "HoneyRealmBot is running!"



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



users = {}


if os.path.exists(USERS_FILE):

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            users = json.load(file)


        if not isinstance(users, dict):

            raise ValueError(
                "Неверный формат users.json"
            )


    except Exception as e:

        logging.error(
            f"Ошибка загрузки users.json: {e}"
        )


        try:

            os.rename(
                USERS_FILE,
                BACKUP_FILE
            )

        except Exception as backup_error:

            logging.error(
                f"Ошибка создания backup: {backup_error}"
            )


        users = {}



def save_users():

    try:

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                users,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        logging.error(
            f"Ошибка сохранения: {e}"
        )



def get_user(user_id):

    user_id = str(user_id)


    if user_id not in users:

        users[user_id] = {
            "collection": []
        }

        save_users()


    return users[user_id]



def get_character(user_id):

    user = get_user(user_id)

    collected = user["collection"]


    available = [

        c for c in characters

        if c["name"] not in collected

    ]


    total = len(characters)

    owned = len(collected)


    if available:

        progress = owned / total


        if progress < 0.5:

            new_chance = 90

        elif progress < 0.8:

            new_chance = 70

        elif progress < 1:

            new_chance = 40

        else:

            new_chance = 0


        roll = random.randint(
            1,
            100
        )


        if roll <= new_chance:

            character = random.choice(
                available
            )

            collected.append(
                character["name"]
            )

            save_users()

            return character



    character = random.choice(
        characters
    )


    return character



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

    user = get_user(
        message.from_user.id
    )


    collected = user["collection"]


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

    user = get_user(
        message.from_user.id
    )


    bot.send_message(

        message.chat.id,

        "🍯 <b>Статистика</b>\n\n"

        f"Получено персонажей: {len(user['collection'])}",

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
