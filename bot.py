import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from PIL import Image

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

accessories = {
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
    },
}

backgrounds = {
    "matrix.png": "Matrix",
    "mario.png": "Mario",
    "windows.png": "Windows",
    "strip.png": "Strip",
    "mlk.png": "MLK",
}

user_choices = {}


def reset_choices(user_id):
    user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    reset_choices(user_id)
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id if update.callback_query else update.message.chat_id
    choices = user_choices[user_id]
    keyboard = [
        [InlineKeyboardButton("Hand", callback_data="menu_hand")],
        [InlineKeyboardButton("Head", callback_data="menu_head")],
        [InlineKeyboardButton("Leg", callback_data="menu_leg")],
        [InlineKeyboardButton("Background", callback_data="menu_background")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
    ]
    message = f"Your selections:\nHand: {choices['hand']}\nHead: {choices['head']}\nLeg: {choices['leg']}\nBackground: {choices['background']}"
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    choices = user_choices[user_id]
    base_image = Image.open("base.png")
    for category, choice in choices.items():
        if choice:
            accessory = accessories[category][choice]
            accessory_image = Image.open(f"{category}/{choice}")
            accessory_image = accessory_image.resize(
                [int(dim * accessory["scale"]) for dim in accessory_image.size]
            )
            base_image.paste(accessory_image, accessory["position"], accessory_image)
    output_path = f"output/result_{user_id}.png"
    base_image.save(output_path)
    await update.callback_query.message.reply_photo(photo=open(output_path, "rb"))


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    query_data = update.callback_query.data
    if query_data == "reset":
        reset_choices(user_id)
    elif query_data == "random":
        for category in user_choices[user_id]:
            if category != "background":
                user_choices[user_id][category] = random.choice(list(accessories[category].keys()))
            else:
                user_choices[user_id]["background"] = random.choice(list(backgrounds.keys()))
    elif query_data.startswith("menu_"):
        category = query_data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"select_{category}_{name}")]
            for name in accessories[category]
        ]
        keyboard.append([InlineKeyboardButton("Back", callback_data="main_menu")])
        await update.callback_query.edit_message_text(
            f"Choose an item for {category.capitalize()}:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query_data.startswith("select_"):
        _, category, choice = query_data.split("_")
        user_choices[user_id][category] = choice
    elif query_data == "generate":
        await generate_image(update, context)
    await show_main_menu(update, context)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
