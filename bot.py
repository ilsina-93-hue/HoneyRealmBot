import telebot
import json
import random
import os
import threading
from flask import Flask


TOKEN = "8969226485:AAF5agI6z1HHj1pHN4Usj-Q30joFRiHbcQM"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


# Для Render
@app.route("/")
def home():
    return "HoneyRealmBot is running!"


# Загружаем персонажей
with open("characters.json", "r", encoding="utf-8-sig") as file:
    characters = json.load(file)


# /start
@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    button = telebot.types.KeyboardButton(
        "🍯 Узнать, кто я"
    )

    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в HoneyRealm 🍯\nНажми кнопку и узнай своего персонажа!",
        reply_markup=markup
    )


# Кнопка в личке
@bot.message_handler(func=lambda message: message.text == "🍯 Узнать, кто я")
def get_character(message):

    character = random.choice(characters)

    image_name = character["image"]

    image_path = os.path.join(
        os.getcwd(),
        image_name
    )

    caption = (
        f"🍯 <b>{character['name']}</b>\n\n"
        f"<i>{character['description']}</i>"
    )

    if os.path.exists(image_path):

        with open(image_path, "rb") as photo:

            bot.send_photo(
                message.chat.id,
                photo,
                caption=caption,
                parse_mode="HTML"
            )

    else:

        bot.send_message(
            message.chat.id,
            f"Ошибка: не найдена картинка {image_name}"
        )


# Inline для групп
@bot.inline_handler(func=lambda query: True)
def inline_character(query):

    character = random.choice(characters)

    image_name = character["image"]


    image_url = (
        "https://raw.githubusercontent.com/"
        "ilsina-93-hue/HoneyRealmBot/main/"
        f"{image_name}"
    )


    caption = (
        f"🍯 <b>{character['name']}</b>\n\n"
        f"<i>{character['description']}</i>"
    )


    # Кнопка под картинкой
    keyboard = telebot.types.InlineKeyboardMarkup()


    button = telebot.types.InlineKeyboardButton(
        text="🍯 Узнать своего персонажа",
        switch_inline_query_current_chat=""
    )


    keyboard.add(button)



    result = telebot.types.InlineQueryResultPhoto(

        id=str(random.randint(100000, 999999999)),

        photo_url=image_url,

        thumbnail_url=image_url,

        caption=caption,

        parse_mode="HTML",

        reply_markup=keyboard
    )


    bot.answer_inline_query(

        query.id,

        results=[result],

        cache_time=0,

        is_personal=True

    )



# Flask поток
def run_flask():

    app.run(
        host="0.0.0.0",
        port=10000
    )



print("HoneyRealmBot запущен!")


threading.Thread(
    target=run_flask
).start()



bot.infinity_polling(
    skip_pending=True
)
