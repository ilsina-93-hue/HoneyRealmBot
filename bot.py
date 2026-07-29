import telebot
import json
import random
import os
import threading
import time
from flask import Flask


TOKEN = "8969226485:AAE7r92E1iz0hRn0zK9pRURTqkwyPgzeBeo"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


# ==========================
# Render
# ==========================

@app.route("/")
def home():
    return "HoneyRealmBot is running!"


# ==========================
# Загружаем персонажей
# ==========================

with open("characters.json", "r", encoding="utf-8-sig") as file:
    characters = json.load(file)


# ==========================
# Отправка персонажа
# ==========================

def send_character(chat_id):

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


    print(
        f"[INFO] Выбран персонаж: {character['name']} "
        f"для {chat_id}"
    )


    if not os.path.exists(image_path):

        print(
            f"[ERROR] Нет картинки: {image_name}"
        )

        bot.send_message(
            chat_id,
            f"Не найдена картинка {image_name}"
        )

        return



    # 2 попытки отправки

    for attempt in range(2):

        try:

            print(
                f"[INFO] Отправка фото. Попытка {attempt + 1}"
            )


            with open(image_path, "rb") as photo:

                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption,
                    parse_mode="HTML",
                    timeout=60
                )


            print(
                "[OK] Фото отправлено успешно"
            )

            return


        except Exception as e:

            print(
                f"[ERROR] Ошибка отправки: {e}"
            )


            if attempt == 0:

                print(
                    "[INFO] Повтор через 2 секунды"
                )

                time.sleep(2)



    # если обе попытки провалились

    bot.send_message(
        chat_id,
        "⚠️ Не удалось отправить персонажа. Попробуйте еще раз."
    )



# ==========================
# /start
# ==========================

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
        "Нажми кнопку ниже или используй /honey в группе.",
        reply_markup=markup
    )



# ==========================
# Кнопка
# ==========================

@bot.message_handler(
    func=lambda message:
    message.text == "🍯 Узнать, кто я"
)
def button_character(message):

    send_character(
        message.chat.id
    )



# ==========================
# Группы
# ==========================

@bot.message_handler(
    commands=["honey"]
)
def honey(message):

    send_character(
        message.chat.id
    )



# ==========================
# Inline
# ==========================

@bot.inline_handler(
    func=lambda query: True
)
def inline_help(query):


    result = telebot.types.InlineQueryResultArticle(

        id="openbot",

        title="🍯 HoneyRealmBot",

        description="Узнать своего персонажа",

        input_message_content=
        telebot.types.InputTextMessageContent(

            message_text=
            "🍯 HoneyRealmBot\n\n"
            "Чтобы узнать своего персонажа:\n\n"
            "• В личном чате нажмите кнопку "
            "«🍯 Узнать, кто я»\n"
            "• В группе используйте:\n"
            "/honey"

        )

    )


    bot.answer_inline_query(

        query.id,

        [result],

        cache_time=0,

        is_personal=True

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



print(
    "HoneyRealmBot запущен!"
)



threading.Thread(

    target=run_flask,

    daemon=True

).start()



bot.infinity_polling(

    skip_pending=True

)
