import telebot
import json
import random
import os

TOKEN = "8969226485:AAHljM-FRo6Cl4d595s3hqjFC-fSrBbmBn4"

bot = telebot.TeleBot(TOKEN)

# Загружаем персонажей (работает с BOM и без BOM)
with open("characters.json", "r", encoding="utf-8-sig") as file:
    characters = json.load(file)


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
    character = random.choice(characters)

    image_name = character["image"]

    # Картинки лежат рядом с bot.py
    image_path = os.path.join(os.getcwd(), image_name)

    if os.path.exists(image_path):
        with open(image_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=f"🍯 {character['name']}\n\n{character['description']}"
            )
    else:
        bot.send_message(
            message.chat.id,
            f"Ошибка: не найдена картинка {image_name}"
        )


print("HoneyRealmBot запущен!")

bot.infinity_polling()
