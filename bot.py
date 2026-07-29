import telebot
import json
import random
import os

TOKEN = "8969226485:AAHljM-FRo6Cl4d595s3hqjFC-fSrBbmBn4"

bot = telebot.TeleBot(TOKEN)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "characters.json")
IMAGES_DIR = os.path.join(BASE_DIR, "images")


@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "🍯 Добро пожаловать в Медовое Царство!\n\n"
        "Нажми кнопку ниже и узнай, кем из жителей ты бы стал."
    )

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🍯 Узнать, кто я")

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "🍯 Узнать, кто я")
def who(message):
    try:
        with open(JSON_FILE, "r", encoding="utf-8-sig") as f:
            characters = json.load(f)

        if not characters:
            bot.send_message(
                message.chat.id,
                "🍯 Медовое Царство пока заселяется..."
            )
            return

        character = random.choice(characters)

        photo_path = os.path.join(
            IMAGES_DIR,
            character["image"]
        )

        caption = (
            f"🍯 <b>Ты - {character['name']}!</b>\n\n"
            f"<i>{character['description']}</i>"
        )

        with open(photo_path, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=caption,
                parse_mode="HTML"
            )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Ошибка:\n{e}"
        )


print("HoneyRealmBot запущен!")

bot.infinity_polling()