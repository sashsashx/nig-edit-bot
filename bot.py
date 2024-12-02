import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from PIL import Image

# Папки с ресурсами
BASE_DIR = "assets"
OUTPUT_DIR = "output"
BASE_IMAGE_PATH = os.path.join(BASE_DIR, "base.png")
CATEGORIES = {
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

# Состояния пользователей
user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Стартовое меню"""
    user_id = update.effective_user.id
    user_states[user_id] = {category: None for category in CATEGORIES}
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню"""
    user_id = update.effective_user.id
    selected = user_states[user_id]
    buttons = [
        [InlineKeyboardButton(f"Hand: {selected['hand'] or 'None'}", callback_data="menu_hand")],
        [InlineKeyboardButton(f"Head: {selected['head'] or 'None'}", callback_data="menu_head")],
        [InlineKeyboardButton(f"Leg: {selected['leg'] or 'None'}", callback_data="menu_leg")],
        [InlineKeyboardButton("Randomize", callback_data="randomize")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if update.callback_query:
        await update.callback_query.edit_message_text("Main Menu", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Main Menu", reply_markup=reply_markup)


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора категории"""
    category = update.callback_query.data.split("_")[1]
    user_id = update.effective_user.id
    buttons = [
        [
            InlineKeyboardButton(item, callback_data=f"select_{category}_{item}")
            for item in CATEGORIES[category]
        ],
        [InlineKeyboardButton("Back", callback_data="main_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.callback_query.edit_message_text(f"Select {category.capitalize()}", reply_markup=reply_markup)


async def select_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора элемента"""
    _, category, item = update.callback_query.data.split("_")
    user_id = update.effective_user.id
    user_states[user_id][category] = item
    await show_main_menu(update, context)


async def randomize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Случайный выбор"""
    import random

    user_id = update.effective_user.id
    for category in CATEGORIES:
        user_states[user_id][category] = random.choice(list(CATEGORIES[category].keys()))
    await show_main_menu(update, context)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сброс выбора"""
    user_id = update.effective_user.id
    user_states[user_id] = {category: None for category in CATEGORIES}
    await show_main_menu(update, context)


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация изображения"""
    user_id = update.effective_user.id
    selections = user_states[user_id]

    try:
        base = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        for category, item in selections.items():
            if item:
                accessory_path = os.path.join(BASE_DIR, category, item)
                accessory = Image.open(accessory_path).convert("RGBA")
                config = CATEGORIES[category][item]
                accessory = accessory.resize(
                    (int(accessory.width * config["scale"]), int(accessory.height * config["scale"]))
                )
                base.paste(accessory, tuple(config["position"]), accessory)

        output_path = os.path.join(OUTPUT_DIR, f"result_{user_id}.png")
        base.save(output_path)
        with open(output_path, "rb") as img:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")


def main():
    """Запуск бота"""
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern="main_menu"))
    app.add_handler(CallbackQueryHandler(handle_category, pattern="menu_"))
    app.add_handler(CallbackQueryHandler(select_item, pattern="select_"))
    app.add_handler(CallbackQueryHandler(randomize, pattern="randomize"))
    app.add_handler(CallbackQueryHandler(reset, pattern="reset"))
    app.add_handler(CallbackQueryHandler(generate_image, pattern="generate"))

    app.run_polling()


if __name__ == "__main__":
    main()
