import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image
import random

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://nig-edit-bot.onrender.com/webhook"

# Путь к изображениям
BASE_IMAGE = "images/nig.png"
ACCESSORY_PATHS = {
    "hand": {
        "phantom": {"path": "images/hand/phantom.png", "position": [3, 242], "scale": 0.3},
        "uzi": {"path": "images/hand/uzi.png", "position": [15, 249], "scale": 0.4},
        "cash": {"path": "images/hand/cash.png", "position": [24, 269], "scale": 0.1},
        "us_flag": {"path": "images/hand/US_flag.png", "position": [-22, 137], "scale": 0.2},
    },
    "head": {
        "bk_crown": {"path": "images/head/BK_crown.png", "position": [123, -13], "scale": 0.2},
        "stone_island": {"path": "images/head/stone_island.png", "position": [30, -83], "scale": 0.7},
        "glasses": {"path": "images/head/glasses.png", "position": [92, 120], "scale": 0.3},
        "blunt": {"path": "images/head/blunt.png", "position": [258, 252], "scale": 0.3},
    },
    "leg": {
        "elf": {"path": "images/leg/elf.png", "position": [240, 183], "scale": 0.3},
    },
    "background": {
        "matrix": "images/background/matrix.png",
        "mario": "images/background/mario.png",
        "windows": "images/background/windows.png",
        "mlk": "images/background/MLK.png",
        "strip": "images/background/strip.png",
    },
}

user_choices = {}

# Обработка команды /start
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Hand", callback_data="menu_hand")],
        [InlineKeyboardButton("Head", callback_data="menu_head")],
        [InlineKeyboardButton("Leg", callback_data="menu_leg")],
        [InlineKeyboardButton("Background", callback_data="menu_background")],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a category:", reply_markup=reply_markup)

# Меню выбора аксессуара
async def menu_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_choices:
        user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}

    menu = query.data.split("_")[1]
    items = ACCESSORY_PATHS.get(menu, {})
    keyboard = [
        [InlineKeyboardButton(name.replace("_", " ").capitalize(), callback_data=f"{menu}_{name}")]
        for name in items
    ] + [[InlineKeyboardButton("Back", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Select {menu} accessory:", reply_markup=reply_markup)

# Обработка выбора
async def selection_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    category, item = query.data.split("_")
    if category in ACCESSORY_PATHS and item in ACCESSORY_PATHS[category]:
        user_choices[user_id][category] = item
        await query.edit_message_text(f"Selected: {item.replace('_', ' ').capitalize()}")
    elif category == "random":
        for cat in ["hand", "head", "leg", "background"]:
            items = list(ACCESSORY_PATHS.get(cat, {}).keys())
            if items:
                user_choices[user_id][cat] = random.choice(items)
        await query.edit_message_text("Random accessories selected!")
    elif category == "reset":
        user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
        await query.edit_message_text("Selections reset!")
    elif category == "main":
        await start(update, context)

# Генерация изображения
async def generate_image(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    base_image = Image.open(BASE_IMAGE)
    background_file = user_choices[user_id]["background"]
    if background_file:
        background_path = ACCESSORY_PATHS["background"].get(background_file)
        if background_path:
            background = Image.open(background_path)
            base_image.paste(background, (0, 0))

    for category, selected_item in user_choices[user_id].items():
        if selected_item and category != "background":
            item_info = ACCESSORY_PATHS[category].get(selected_item)
            if item_info:
                accessory = Image.open(item_info["path"])
                accessory = accessory.resize(
                    (
                        int(accessory.width * item_info["scale"]),
                        int(accessory.height * item_info["scale"]),
                    )
                )
                base_image.paste(accessory, tuple(item_info["position"]), accessory)

    output_path = f"output/result_{user_id}.png"
    base_image.save(output_path)
    await query.message.reply_photo(photo=open(output_path, "rb"))

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="menu_.+"))
    application.add_handler(CallbackQueryHandler(selection_handler, pattern="^(hand|head|leg|background|random|reset)_.+"))
    application.add_handler(CallbackQueryHandler(generate_image, pattern="generate"))

    application.run_webhook(
        listen="0.0.0.0",
        port=443,
        webhook_url=WEBHOOK_URL,
        path="/webhook"
    )

if __name__ == "__main__":
    main()
