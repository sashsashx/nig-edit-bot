from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image
import os

# Flask app setup
app = Flask(__name__)

# Telegram bot token
BOT_TOKEN = os.environ.get("BOT_TOKEN")
application = Application.builder().token(BOT_TOKEN).build()

# Global variables to track user choices
user_choices = {}

# Image directories
BASE_IMAGE = "images/nig.png"
HAND_DIR = "images/hand"
HEAD_DIR = "images/head"
BODY_DIR = "images/body"
LEGS_DIR = "images/legs"

# Generate final image
def generate_image(user_id):
    base_image = Image.open(BASE_IMAGE).convert("RGBA")
    if user_id in user_choices:
        for part, accessory in user_choices[user_id].items():
            if accessory:
                part_dir = {
                    "hand": HAND_DIR,
                    "head": HEAD_DIR,
                    "body": BODY_DIR,
                    "legs": LEGS_DIR,
                }[part]
                accessory_image = Image.open(os.path.join(part_dir, accessory)).convert("RGBA")
                if part == "hand":
                    base_image.paste(accessory_image, (100, 200), accessory_image)
                elif part == "head":
                    base_image.paste(accessory_image, (150, 50), accessory_image)
                elif part == "body":
                    base_image.paste(accessory_image, (100, 300), accessory_image)
                elif part == "legs":
                    base_image.paste(accessory_image, (100, 500), accessory_image)
    output_path = f"output_{user_id}.png"
    base_image.save(output_path)
    return output_path

# Command handlers
def start(update: Update, context):
    user_id = update.message.from_user.id
    state = user_choices.get(user_id, {})
    hand_state = state.get("hand", "None")
    head_state = state.get("head", "None")
    body_state = state.get("body", "None")
    legs_state = state.get("legs", "None")

    keyboard = [
        [InlineKeyboardButton(f"Hand [{hand_state}]", callback_data="menu_hand")],
        [InlineKeyboardButton(f"Head [{head_state}]", callback_data="menu_head")],
        [InlineKeyboardButton(f"Body [{body_state}]", callback_data="menu_body")],
        [InlineKeyboardButton(f"Legs [{legs_state}]", callback_data="menu_legs")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a body part to customize:", reply_markup=reply_markup)

def handle_menu(update: Update, context):
    query = update.callback_query
    query.answer()

    if query.data == "menu_hand":
        hand_keyboard = [
            [InlineKeyboardButton("Coffee", callback_data="select_hand_coffee"),
             InlineKeyboardButton("KFC Wings", callback_data="select_hand_kfc")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        query.edit_message_text("Choose an accessory for the hand:",
                                reply_markup=InlineKeyboardMarkup(hand_keyboard))

    elif query.data == "menu_head":
        head_keyboard = [
            [InlineKeyboardButton("MAGA Hat", callback_data="select_head_maga_hat"),
             InlineKeyboardButton("Wif Hat", callback_data="select_head_wif_hat"),
             InlineKeyboardButton("Chrome Hat", callback_data="select_head_chrome_hat")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        query.edit_message_text("Choose an accessory for the head:",
                                reply_markup=InlineKeyboardMarkup(head_keyboard))

    elif query.data == "menu_body":
        body_keyboard = [
            [InlineKeyboardButton("T-shirt", callback_data="select_body_tshirt")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        query.edit_message_text("Choose an accessory for the body:",
                                reply_markup=InlineKeyboardMarkup(body_keyboard))

    elif query.data == "menu_legs":
        legs_keyboard = [
            [InlineKeyboardButton("Jeans", callback_data="select_legs_jeans")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        query.edit_message_text("Choose an accessory for the legs:",
                                reply_markup=InlineKeyboardMarkup(legs_keyboard))

    elif query.data == "reset":
        user_id = query.from_user.id
        user_choices[user_id] = {}
        query.edit_message_text("Choices reset! Use /start to begin again.")

    elif query.data == "generate":
        user_id = query.from_user.id
        image_path = generate_image(user_id)
        query.message.reply_photo(photo=open(image_path, "rb"))
        start(query.message, context)

    elif query.data == "back_to_main":
        start(query.message, context)

def handle_selection(update: Update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    _, part, accessory = query.data.split("_")
    if user_id not in user_choices:
        user_choices[user_id] = {}
    user_choices[user_id][part] = f"{accessory}.png"
    query.edit_message_text(f"You selected: {accessory.capitalize()}")
    start(query.message, context)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
application.add_handler(CallbackQueryHandler(handle_selection, pattern="^select_"))

# Flask webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    json_update = request.get_json()
    update = Update.de_json(json_update, application.bot)
    application.update_queue.put(update)
    return "OK", 200

# Run Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8443))
    app.run(host="0.0.0.0", port=port)
