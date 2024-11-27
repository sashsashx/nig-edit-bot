import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Flask приложение
app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = "7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM"

# Инициализация Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# Обработчики Telegram
async def start(update: Update, context):
    keyboard = [
        [{"text": "Hand", "callback_data": "menu_hand"}],
        [{"text": "Head", "callback_data": "menu_head"}],
        [{"text": "Reset", "callback_data": "reset"}],
        [{"text": "Generate Image", "callback_data": "generate"}],
    ]
    reply_markup = {"inline_keyboard": keyboard}
    await update.message.reply_text("Choose a body part:", reply_markup=reply_markup)

async def menu(update: Update, context):
    query = update.callback_query
    part = query.data.split("_")[1]
    if part == "hand":
        keyboard = [
            [{"text": "Coffee", "callback_data": "select_hand_coffee"}],
            [{"text": "KFC Wings", "callback_data": "select_hand_kfc"}],
            [{"text": "Back", "callback_data": "main_menu"}],
        ]
    elif part == "head":
        keyboard = [
            [{"text": "MAGA Hat", "callback_data": "select_head_maga_hat"}],
            [{"text": "WiF Hat", "callback_data": "select_head_wif_hat"}],
            [{"text": "Chrome Hat", "callback_data": "select_head_chrome_hat"}],
            [{"text": "Back", "callback_data": "main_menu"}],
        ]
    else:
        keyboard = []
    reply_markup = {"inline_keyboard": keyboard}
    await query.edit_message_text(f"Choose an accessory for {part}:", reply_markup=reply_markup)

async def select(update: Update, context):
    query = update.callback_query
    _, part, accessory = query.data.split("_")
    context.user_data[part] = accessory
    await query.edit_message_text(f"You selected: {accessory}")
    await start(update, context)

async def reset(update: Update, context):
    context.user_data.clear()
    await update.callback_query.edit_message_text("Selections reset.")
    await start(update, context)

async def generate(update: Update, context):
    query = update.callback_query
    await query.edit_message_text("Generating image...")
    # Реализация генерации изображения
    await query.edit_message_text("Image generated!")

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(menu, pattern="menu_"))
application.add_handler(CallbackQueryHandler(select, pattern="select_"))
application.add_handler(CallbackQueryHandler(reset, pattern="reset"))
application.add_handler(CallbackQueryHandler(generate, pattern="generate"))
application.add_handler(CallbackQueryHandler(start, pattern="main_menu"))

# Маршрут Flask для вебхука
@app.route("/webhook", methods=["POST"])
def webhook():
    json_update = request.get_json()
    if json_update:
        update = Update.de_json(json_update, application.bot)
        application.update_queue.put(update)
    return "OK", 200

# Запуск Flask
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
