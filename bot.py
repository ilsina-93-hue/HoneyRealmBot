import telebot
import json
import random
import os
import threading
from flask import Flask

TOKEN = "8969226485:AAF5agI6z1HHj1pHN4Usj-Q30joFRiHbcQM"

bot = telebot.TeleBot(TOKEN)

# Загружаем персонажей
with open("characters.json", "r", encoding="utf-8-sig") as file:
    characters = json.load(file)


# -----------------------
# Render Web Server
# -----------------------

app = Flask(__name__)


@app.route("/")
def home():
    return "HoneyRealmBot работает!"


def run_web():
    app.run(host="0.0.0.0", port=10000)


# -----------------------
# Telegram Bot
# -----------------------

@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    button = telebot.types.KeyboardButton("🍯 Узнать, кто я")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "*Добро пожаловать в HoneyRealm* 🍯\n\nНажми кнопку и узнай своего персонажа!",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.message_handler(func=lambda message: message.text == "🍯 Узнать, кто я")
def get_character(message):

    character = random.choice(characters)

    image_name = character["image"]

    image_path = os.path.join(
        os.path.dirname(__file__),
        image_name
    )

    caption = (
        f"🍯 *{character['name']}*\n\n"
        f"_{character['description']}_"
    )

    if os.path.exists(image_path):

        with open(image_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=caption,
                parse_mode="Markdown"
            )

    else:

        bot.send_message(
            message.chat.id,
            f"Ошибка: не найдена картинка {image_name}"
        )


print("HoneyRealmBot запущен!")


# Запускаем порт для Render
threading.Thread(
    target=run_web
).start()


# Запускаем Telegram
bot.infinity_polling()
