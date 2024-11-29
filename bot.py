from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image
import os
import random

# Store user choices
user_choices = {}

# Accessory and background data
ACCESSORY_DATA = {
    "hand": {
        "coffee.png": {"position": [-45, 208], "scale": 0.5},
        "kfc.png": {"position": [0, 221], "scale": 0.3},
        "uzi.png": {"position": [15, 249], "scale": 0.4},
        "cash.png": {"position": [24, 269], "scale": 0.1},
        "phantom.png": {"position": [3, 242], "scale": 0.3},
        "US_flag.png": {"position": [-22, 137], "scale": 0.2},
    },
    "head": {
        "maga_hat.png": {"position": [0, -15], "scale": 0.5},
        "wif_hat.png": {"position": [45, -43], "scale": 0.7},
        "chrome_hat.png": {"position": [70, -29], "scale": 0.3},
        "stone_island.png": {"position": [30, -83], "scale": 0.7},
        "blunt.png": {"position": [258, 252], "scale": 0.3},
        "glasses.png": {"position": [92, 120], "scale": 0.3},
        "BK_crown.png": {"position": [123, -13], "scale": 0.2},
    },
    "leg": {
        "elf.png": {"position": [240, 183], "scale": 0.3},
        "skate.png": {"position": [19, 225], "scale": 0.9},
    }
}

BACKGROUND_DATA = ["matrix", "mario", "windows", "MCD", "strip", "MLK"]

# Start command
async def start(update: Update, context):
    user_id = update.effective_user.id
    user_choices[user_id] = user_choices.get(user_id, {"hand": None, "head": None, "leg": None, "background": None})

    keyboard = [
        [InlineKeyboardButton(f"Hand (Selected: {user_choices[user_id]['hand'] or 'None'})", callback_data="menu_hand")],
        [InlineKeyboardButton(f"Head (Selected: {user_choices[user_id]['head'] or 'None'})", callback_data="menu_head")],
        [InlineKeyboardButton(f"Leg (Selected: {user_choices[user_id]['leg'] or 'None'})", callback_data="menu_leg")],
        [InlineKeyboardButton(f"Background (Selected: {user_choices[user_id]['background'] or 'None'})", callback_data="menu_background")],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Generate", callback_data="generate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Customize your image:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text("Customize your image:", reply_markup=reply_markup)

# Menu handler
async def menu_handler(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "menu_hand":
        keyboard = [
            [InlineKeyboardButton("Coffee", callback_data="hand_coffee")],
            [InlineKeyboardButton("KFC Wings", callback_data="hand_kfc")],
            [InlineKeyboardButton("Uzi", callback_data="hand_uzi")],
            [InlineKeyboardButton("Cash", callback_data="hand_cash")],
            [InlineKeyboardButton("Phantom", callback_data="hand_phantom")],
            [InlineKeyboardButton("US Flag", callback_data="hand_US_flag")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose an accessory for the hand:", reply_markup=reply_markup)

    elif query.data == "menu_head":
        keyboard = [
            [InlineKeyboardButton("MAGA Hat", callback_data="head_maga_hat")],
            [InlineKeyboardButton("WIF Hat", callback_data="head_wif_hat")],
            [InlineKeyboardButton("Chrome Hat", callback_data="head_chrome_hat")],
            [InlineKeyboardButton("Stone Island", callback_data="head_stone_island")],
            [InlineKeyboardButton("Blunt", callback_data="head_blunt")],
            [InlineKeyboardButton("Glasses", callback_data="head_glasses")],
            [InlineKeyboardButton("BK Crown", callback_data="head_BK_crown")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose an accessory for the head:", reply_markup=reply_markup)

    elif query.data == "menu_leg":
        keyboard = [
            [InlineKeyboardButton("Elf", callback_data="leg_elf")],
            [InlineKeyboardButton("Skate", callback_data="leg_skate")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose an accessory for the leg:", reply_markup=reply_markup)

    elif query.data == "menu_background":
        keyboard = [
            [InlineKeyboardButton("Matrix", callback_data="background_matrix")],
            [InlineKeyboardButton("Mario", callback_data="background_mario")],
            [InlineKeyboardButton("Windows", callback_data="background_windows")],
            [InlineKeyboardButton("MCD", callback_data="background_MCD")],
            [InlineKeyboardButton("Strip", callback_data="background_strip")],
            [InlineKeyboardButton("MLK", callback_data="background_MLK")],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose a background:", reply_markup=reply_markup)

    elif query.data == "reset":
        user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
        await query.edit_message_text("Selections have been reset.")
        await start(update, context)

    elif query.data == "random":
        user_choices[user_id]["hand"] = random.choice(list(ACCESSORY_DATA["hand"].keys()))
        user_choices[user_id]["head"] = random.choice(list(ACCESSORY_DATA["head"].keys()))
        user_choices[user_id]["leg"] = random.choice(list(ACCESSORY_DATA["leg"].keys()))
        user_choices[user_id]["background"] = random.choice(BACKGROUND_DATA)
        await start(update, context)

    elif query.data == "generate":
        await query.edit_message_text("Generating image...")
        await generate_image(user_id, query)

    elif query.data == "back":
        await start(update, context)

# Generate the final image
async def generate_image(user_id, query):
    try:
        base_image = Image.open("images/nig.png").convert("RGBA")
        result_image = Image.new("RGBA", base_image.size, (255, 255, 255, 255))

        background_file = user_choices[user_id].get("background")
        if background_file:
            background_path = f"images/background/{background_file}.png"
            if os.path.exists(background_path):
                background_image = Image.open(background_path).convert("RGBA").resize(base_image.size)
                result_image.paste(background_image, (0, 0))
            else:
                await query.message.reply_text(f"Error: Background '{background_file}' not found!")
                return

        result_image.paste(base_image, (0, 0), base_image)

        for part, accessory_file in user_choices[user_id].items():
            if part in ACCESSORY_DATA and accessory_file and accessory_file in ACCESSORY_DATA[part]:
                accessory_path = f"images/{part}/{accessory_file}"
                accessory_image = Image.open(accessory_path).convert("RGBA")
                data = ACCESSORY_DATA[part][accessory_file]
                position = data["position"]
                scale = data["scale"]
                accessory_image = accessory_image.resize(
                    (int(accessory_image.width * scale), int(accessory_image.height * scale))
                )
                result_image.paste(accessory_image, position, accessory_image)

        output_path = f"output/result_{user_id}.png"
        result_image.save(output_path)
        await query.message.reply_photo(photo=open(output_path, 'rb'))
    except Exception as e:
        await query.message.reply_text(f"Error during generation: {str(e)}")

# Main function to start the bot
def main():
    application = Application.builder().token("7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_.*$|^reset$|^generate$|^random$|^back$"))
    application.add_handler(CallbackQueryHandler(selection_handler, pattern="^(hand|head|leg|background)_.+"))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="webhook",
        webhook_url="https://nig-edit-bot.onrender.com/webhook",
    )

if __name__ == "__main__":
    main()
