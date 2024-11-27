from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image
import os

# Telegram bot token
BOT_TOKEN = "7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM"

# Initialize the bot
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
    base_image = Image.open(BASE_IMAGE)
    if user_id in user_choices:
        for part, accessory in user_choices[user_id].items():
            if accessory:
                if part == "hand":
                    part_dir = HAND_DIR
                    position = (100, 200)
                elif part == "head":
                    part_dir = HEAD_DIR
                    position = (150, 50)
                elif part == "body":
                    part_dir = BODY_DIR
                    position = (100, 100)
                elif part == "legs":
                    part_dir = LEGS_DIR
                    position = (100, 300)

                accessory_image = Image.open(os.path.join(part_dir, accessory))
                base_image.paste(accessory_image, position, accessory_image)
    output_path = f"output_{user_id}.png"
    base_image.save(output_path)
    return output_path

# Command handlers
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Hand", callback_data="menu_hand"),
         InlineKeyboardButton("Head", callback_data="menu_head")],
        [InlineKeyboardButton("Body", callback_data="menu_body"),
         InlineKeyboardButton("Legs", callback_data="menu_legs")],
        [InlineKeyboardButton("Reset", callback_data="reset"),
         InlineKeyboardButton("Generate", callback_data="generate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a body part to customize:", reply_markup=reply_markup)

async def handle_menu(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_hand":
        hand_keyboard = [
            [InlineKeyboardButton("Coffee", callback_data="select_hand_coffee"),
             InlineKeyboardButton("KFC Wings", callback_data="select_hand_kfc")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text("Choose an accessory for the hand:",
                                       reply_markup=InlineKeyboardMarkup(hand_keyboard))

    elif query.data == "menu_head":
        head_keyboard = [
            [InlineKeyboardButton("MAGA Hat", callback_data="select_head_maga_hat"),
             InlineKeyboardButton("Wif Hat", callback_data="select_head_wif_hat"),
             InlineKeyboardButton("Chrome Hat", callback_data="select_head_chrome_hat")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text("Choose an accessory for the head:",
                                       reply_markup=InlineKeyboardMarkup(head_keyboard))

    elif query.data == "menu_body":
        body_keyboard = [
            [InlineKeyboardButton("Jacket", callback_data="select_body_jacket"),
             InlineKeyboardButton("Tie", callback_data="select_body_tie")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text("Choose an accessory for the body:",
                                       reply_markup=InlineKeyboardMarkup(body_keyboard))

    elif query.data == "menu_legs":
        legs_keyboard = [
            [InlineKeyboardButton("Boots", callback_data="select_legs_boots"),
             InlineKeyboardButton("Jeans", callback_data="select_legs_jeans")],
            [InlineKeyboardButton("Back", callback_data="back_to_main")]
        ]
        await query.edit_message_text("Choose an accessory for the legs:",
                                       reply_markup=InlineKeyboardMarkup(legs_keyboard))

    elif query.data == "reset":
        user_choices[query.from_user.id] = {}
        await query.edit_message_text("Choices reset! Use /start to begin again.")

    elif query.data == "generate":
        user_id = query.from_user.id
        image_path = generate_image(user_id)
        await query.message.reply_photo(photo=open(image_path, "rb"))

    elif query.data == "back_to_main":
        await start(query.message, context)

async def handle_selection(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Parse the selection
    _, part, accessory = query.data.split("_")
    if user_id not in user_choices:
        user_choices[user_id] = {}
    user_choices[user_id][part] = f"{accessory}.png"

    await query.edit_message_text(f"You selected: {accessory.capitalize()}")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_menu, pattern="^menu_"))
application.add_handler(CallbackQueryHandler(handle_selection, pattern="^select_"))

# Run the bot with polling
if __name__ == "__main__":
    application.run_polling()
