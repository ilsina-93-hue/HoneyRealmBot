import telebot
import json
import random
import os
import time

TOKEN = "8969226485:AAF5agI6z1HHj1pHN4Usj-Q30joFRiHbcQM"

bot = telebot.TeleBot(TOKEN)


# Загружаем персонажей (BOM и обычный UTF-8)
try:
    with open("characters.json", "r", encoding="utf-8-sig") as file:
        characters = json.load(file)
except Exception as e:
    print("Ошибка загрузки characters.json:", e)
    characters = []


@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("🍯 Узнать, кто я")
    markup.add(button)

    bot.send_message(
        message.chat.id,
        "Добро пожаловать в HoneyRealm 🍯\nНажми кнопку и узнай своего персонажа!",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "🍯 Узнать, кто я")
def get_character(message):
    if not characters:
        bot.send_message(
            message.chat.id,
            "Персонажи пока не загружены."
        )
        return

    character = random.choice(characters)

    image_name = character["image"]
    image_path = os.path.join(
        os.path.dirname(__file__),
        image_name
    )

    caption = (
        f"🍯 {character['name']}\n\n"
        f"{character['description']}"
    )

    if os.path.exists(image_path):
        with open(image_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=caption
            )
    else:
        bot.send_message(
            message.chat.id,
            f"Ошибка: не найдена картинка {image_name}"
        )


print("HoneyRealmBot запущен!")


while True:
    try:
        bot.infinity_polling(
            timeout=60,
            long_polling_timeout=60
        )
    except Exception as e:
        print("Ошибка polling:", e)
        time.sleep(5)
