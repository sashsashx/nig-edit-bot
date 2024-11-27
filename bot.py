import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, Dispatcher
from PIL import Image

# Flask приложение
app = Flask(__name__)

# Telegram Bot Application
application = Application.builder().token("7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM").build()

# Telegram Dispatcher для обработки обновлений
dispatcher: Dispatcher = application.dispatcher

# Хранилище для пользовательских выборов
user_choices = {}

# Определение аксессуаров для частей тела
ACCESSORIES = {
    "hand": {"coffee": "Coffee", "kfc": "KFC Wings"},
    "head": {"maga_hat": "MAGA Hat", "wif_hat": "WIF Hat", "chrome_hat": "Chrome Hat"},
    "torso": {},  # Пока пусто
    "legs": {},   # Пока пусто
}

# Команда /start
async def start(update: Update, context):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    keyboard = [
        [
            InlineKeyboardButton(
                f"Hand [{user_choices.get(user_id, {}).get('hand', 'None')}]",
                callback_data="menu_hand",
            )
        ],
        [
            InlineKeyboardButton(
                f"Head [{user_choices.get(user_id, {}).get('head', 'None')}]",
                callback_data="menu_head",
            )
        ],
        [
            InlineKeyboardButton(f"Torso [None]", callback_data="menu_torso"),
            InlineKeyboardButton(f"Legs [None]", callback_data="menu_legs"),
        ],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Choose a body part:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Choose a body part:", reply_markup=reply_markup)

# Меню аксессуаров
async def menu(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    part = query.data.split("_")[1]

    accessories = ACCESSORIES.get(part, {})
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"select_{part}_{key}")]
        for key, name in accessories.items()
    ]
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(f"Choose an accessory for {part.capitalize()}:", reply_markup=reply_markup)

# Выбор аксессуара
async def select(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        _, part, accessory = query.data.split("_")
        if accessory not in ACCESSORIES.get(part, {}):
            await query.answer("Invalid accessory selected!")
            return
    except ValueError:
        await query.answer("Invalid selection!")
        return

    if user_id not in user_choices:
        user_choices[user_id] = {}
    user_choices[user_id][part] = ACCESSORIES[part][accessory]

    await start(update, context)

# Сброс выборов
async def reset(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    user_choices[user_id] = {}
    await start(update, context)

# Генерация изображения
async def generate(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    base_image = Image.open("images/nig.png")
    positions = {
        "hand": (60, 300),
        "head": (175, 50),
    }

    for part, accessory in user_choices.get(user_id, {}).items():
        if accessory:
            accessory_image = Image.open(f"images/{part}/{accessory}.png").resize((150, 150))
            base_image.paste(accessory_image, positions[part], accessory_image)

    output_path = f"images/result_{user_id}.png"
    base_image.save(output_path)
    await query.message.reply_photo(photo=open(output_path, "rb"))

# Добавление обработчиков
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CallbackQueryHandler(menu, pattern="menu_"))
dispatcher.add_handler(CallbackQueryHandler(select, pattern="select_"))
dispatcher.add_handler(CallbackQueryHandler(reset, pattern="reset"))
dispatcher.add_handler(CallbackQueryHandler(generate, pattern="generate"))
dispatcher.add_handler(CallbackQueryHandler(start, pattern="main_menu"))

# Маршрут для вебхука
@app.route("/webhook", methods=["POST"])
def webhook():
    json_update = request.get_json()
    if json_update:
        update = Update.de_json(json_update, application.bot)
        dispatcher.process_update(update)
    return "OK", 200

# Основная функция для запуска Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
