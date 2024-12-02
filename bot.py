import os
import logging
import random
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from PIL import Image

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

# Пути к ресурсам
BASE_IMAGE_PATH = "images/nig.png"
HAND_ACCESSORIES = {
    "Coffee": "images/hand/coffee.png",
    "KFC": "images/hand/kfc.png",
    "Uzi": "images/hand/uzi.png",
    "Cash": "images/hand/cash.png",
    "Phantom": "images/hand/phantom.png",
    "US Flag": "images/hand/US_flag.png",
}
HEAD_ACCESSORIES = {
    "Maga Hat": "images/head/maga_hat.png",
    "WIF Hat": "images/head/wif_hat.png",
    "Chrome Hat": "images/head/chrome_hat.png",
    "Stone Island": "images/head/stone_island.png",
    "Blunt": "images/head/blunt.png",
    "Glasses": "images/head/glasses.png",
    "BK Crown": "images/head/BK_crown.png",
}
LEG_ACCESSORIES = {
    "Elf": "images/leg/elf.png",
    "Skate": "images/leg/skate.png",
}
BACKGROUNDS = {
    "Matrix": "images/background/matrix.png",
    "Mario": "images/background/mario.png",
    "Windows": "images/background/windows.png",
    "Strip": "images/background/strip.png",
    "MLK": "images/background/MLK.png",
}

# Хранилище данных пользователей
user_data = {}

# Команда /start
async def start(update: Update, context):
    user_id = get_user_id(update)
    user_data[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
    await show_main_menu(update, context)

# Получение user_id
def get_user_id(update: Update):
    if update.message:
        return update.message.from_user.id
    elif update.callback_query:
        return update.callback_query.from_user.id
    return None

# Отображение главного меню
async def show_main_menu(update: Update, context):
    user_id = get_user_id(update)
    selections = user_data.get(user_id, {})
    keyboard = [
        [
            InlineKeyboardButton(
                f"Hand [{selections.get('hand', 'None')}]",
                callback_data="menu_hand",
            )
        ],
        [
            InlineKeyboardButton(
                f"Head [{selections.get('head', 'None')}]",
                callback_data="menu_head",
            )
        ],
        [
            InlineKeyboardButton(
                f"Leg [{selections.get('leg', 'None')}]",
                callback_data="menu_leg",
            )
        ],
        [
            InlineKeyboardButton(
                f"Background [{selections.get('background', 'None')}]",
                callback_data="menu_background",
            )
        ],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Choose a category:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "Choose a category:", reply_markup=reply_markup
        )

# Обработчик выбора
async def selection_handler(update: Update, context):
    query = update.callback_query
    user_id = get_user_id(update)
    user_data.setdefault(user_id, {"hand": None, "head": None, "leg": None, "background": None})

    await query.answer()
    if query.data.startswith("menu_"):
        category = query.data.split("_")[1]
        options = {
            "hand": HAND_ACCESSORIES,
            "head": HEAD_ACCESSORIES,
            "leg": LEG_ACCESSORIES,
            "background": BACKGROUNDS,
        }.get(category, {})
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"{category}_{name}")]
            for name in options
        ] + [[InlineKeyboardButton("Back", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"Select an item for {category.capitalize()}:", reply_markup=reply_markup
        )
    elif query.data.startswith(("hand_", "head_", "leg_", "background_")):
        category, item = query.data.split("_", 1)
        user_data[user_id][category] = item
        await show_main_menu(update, context)
    elif query.data == "random":
        user_data[user_id] = {
            "hand": random.choice(list(HAND_ACCESSORIES.keys())),
            "head": random.choice(list(HEAD_ACCESSORIES.keys())),
            "leg": random.choice(list(LEG_ACCESSORIES.keys())),
            "background": random.choice(list(BACKGROUNDS.keys())),
        }
        await show_main_menu(update, context)
    elif query.data == "generate":
        await query.edit_message_text("Generating image...")
        await generate_image(user_id, context, query)
    elif query.data == "reset":
        user_data[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
        await show_main_menu(update, context)
    elif query.data == "main_menu":
        await show_main_menu(update, context)

# Генерация изображения
async def generate_image(user_id, context, query):
    try:
        logger.info(f"Начинаем генерацию изображения для пользователя {user_id}")
        base_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        selections = user_data[user_id]
        
        for category, items in [("hand", HAND_ACCESSORIES), ("head", HEAD_ACCESSORIES), ("leg", LEG_ACCESSORIES)]:
            if selections[category]:
                image_path = items[selections[category]]
                accessory = Image.open(image_path).convert("RGBA")
                base_image.paste(accessory, (0, 0), accessory)

        output_path = f"output/result_{user_id}.png"
        base_image.save(output_path)
        await query.message.reply_photo(photo=open(output_path, "rb"))
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        await query.message.reply_text("Ошибка генерации изображения. Попробуйте снова.")

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(selection_handler, pattern=".*"))

    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url=f"{APP_URL}/webhook",
    )

if __name__ == "__main__":
    main()
