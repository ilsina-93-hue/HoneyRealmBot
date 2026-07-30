import telebot
import json
import random
import os
import threading
import time
import logging
from flask import Flask


TOKEN = "8969226485:AAHCI6TcrCjEj3XgaC-BfndGMMVjCI2nUhc"


bot = telebot.TeleBot(TOKEN)


app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


CHARACTERS_FILE = "characters.json"
USERS_FILE = "users.json"


# ==========================
# Flask
# ==========================

@app.route("/")
def home():
    return "HoneyRealmBot is running!"



# ==========================
# Загрузка персонажей
# ==========================

with open(
    CHARACTERS_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    characters = json.load(file)



# ==========================
# Пользователи
# ==========================

if os.path.exists(USERS_FILE):

    with open(
        USERS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        users = json.load(file)

else:

    users = {}



def save_users():

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



# ==========================
# Получение пользователя
# ==========================

def get_user(user_id):

    user_id = str(user_id)

    if user_id not in users:

        users[user_id] = {

            "collection": []

        }

        save_users()


    return users[user_id]



# ==========================
# Выбор персонажа
# ==========================

def get_character(user_id):

    user = get_user(user_id)


    collected = user["collection"]


    available = [

        c for c in characters

        if c["name"] not in collected

    ]


    if len(available) == 0:

        available = characters



    character = random.choice(
        available
    )


    if character["name"] not in collected:

        collected.append(
            character["name"]
        )

        save_users()


    return character
    ```python
# ==========================
# Отправка персонажа
# ==========================

def send_character(message):

    user_id = message.from_user.id

    character = get_character(
        user_id
    )


    image_name = character["image"]


    image_path = os.path.join(
        os.getcwd(),
        image_name
    )


    caption = (

        f"🍯 <b>{character['name']}</b>\n\n"

        f"<i>{character['description']}</i>\n\n"

        f"📖 Новый персонаж добавлен в коллекцию!"

    )


    logging.info(

        f"{message.from_user.id} получил {character['name']}"

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


        bot.send_message(

            message.chat.id,

            "⚠️ Ошибка отправки персонажа."

        )



# ==========================
# Коллекция
# ==========================

@bot.message_handler(
    commands=["collection"]
)
def collection(message):

    user = get_user(
        message.from_user.id
    )


    collected = user["collection"]


    total = len(characters)

    opened = len(collected)


    text = (

        "🍯 <b>Твоя коллекция HoneyRealm</b>\n\n"

        f"Открыто: {opened}/{total}\n\n"

    )


    if opened == 0:

        text += "Коллекция пока пуста."


    else:

        for index, name in enumerate(
            collected,
            start=1
        ):

            text += (

                f"{index}. {name}\n"

            )


    bot.send_message(

        message.chat.id,

        text,

        parse_mode="HTML"

    )



# ==========================
# Статистика
# ==========================

@bot.message_handler(
    commands=["stats"]
)
def stats(message):

    user = get_user(
        message.from_user.id
    )


    count = len(
        user["collection"]
    )


    bot.send_message(

        message.chat.id,

        "🍯 <b>Статистика</b>\n\n"
        f"Получено персонажей: {count}",

        parse_mode="HTML"

    )



# ==========================
# /start
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
        "Получай персонажей и собирай коллекцию.",

        reply_markup=markup

    )
# ==========================
# Кнопка получения персонажа
# ==========================

@bot.message_handler(
    func=lambda message:
    message.text == "🍯 Узнать, кто я"
)
def button_character(message):

    send_character(
        message
    )



# ==========================
# Команда /honey
# ==========================

@bot.message_handler(
    commands=["honey"]
)
def honey(message):

    send_character(
        message
    )



# ==========================
# Помощь
# ==========================

@bot.message_handler(
    commands=["help"]
)
def help_command(message):

    bot.send_message(

        message.chat.id,

        "🍯 <b>HoneyRealmBot</b>\n\n"

        "Команды:\n\n"

        "/honey — получить персонажа\n"
        "/collection — открыть коллекцию\n"
        "/stats — статистика\n"
        "/help — помощь",

        parse_mode="HTML"

    )



# ==========================
# Неизвестные команды
# ==========================

@bot.message_handler(
    func=lambda message:
    message.text is not None
    and message.text.startswith("/")
)
def unknown_command(message):

    bot.send_message(

        message.chat.id,

        "❌ Такой команды нет.\n"
        "Используйте /help."

    )



# ==========================
# Flask запуск
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



# ==========================
# Telegram polling
# ==========================

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

            f"Polling ошибка: {e}"

        )


        time.sleep(10)
