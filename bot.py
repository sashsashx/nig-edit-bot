import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_URL = os.getenv("APP_URL")

# Пути к изображениям
BASE_IMAGE_PATH = "images/nig.png"
HAND_ACCESSORIES = {
    "Phantom": "images/hand/phantom.png",
    "Uzi": "images/hand/uzi.png",
    "Cash": "images/hand/cash.png",
    "US Flag": "images/hand/US_flag.png",
    "KFC": "images/hand/kfc.png",
}
HEAD_ACCESSORIES = {
    "Stone Island": "images/head/stone_island.png",
    "Blunt": "images/head/blunt.png",
    "Glasses": "images/head/glasses.png",
    "BK Crown": "images/head/BK_crown.png",
    "Maga Hat": "images/head/maga_hat.png",
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
    user_id = update.message.chat_id if update.message else update.callback_query.from_user.id
    user_data[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
    await show_main_menu(update, context)

# Главное меню
async def show_main_menu(update: Update, context):
    user_id = None
    if hasattr(update, "message") and update.message:
        user_id = update.message.chat_id
    elif hasattr(update, "callback_query") and update.callback_query:
        user_id = update.callback_query.from_user.id
    
    if user_id is None:
        logger.error("Не удалось определить user_id")
        await update.callback_query.answer("Произошла ошибка. Попробуйте еще раз.", show_alert=True)
        return

    data = user_data.get(user_id, {})
    keyboard = [
        [InlineKeyboardButton(f"Hand [{data.get('hand') or 'None'}]", callback_data="menu_hand")],
        [InlineKeyboardButton(f"Head [{data.get('head') or 'None'}]", callback_data="menu_head")],
        [InlineKeyboardButton(f"Leg [{data.get('leg') or 'None'}]", callback_data="menu_leg")],
        [InlineKeyboardButton(f"Background [{data.get('background') or 'None'}]", callback_data="menu_background")],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
        [InlineKeyboardButton("Reset", callback_data="reset")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if hasattr(update, "message") and update.message:
        await update.message.reply_text("Main Menu:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("Main Menu:", reply_markup=reply_markup)

# Обработчик выбора
async def selection_handler(update: Update, context):
    query = update.callback_query
    if query is None:
        logger.error("CallbackQuery отсутствует в update")
        return

    user_id = query.from_user.id
    user_data.setdefault(user_id, {"hand": None, "head": None, "leg": None, "background": None})
    await query.answer()

    try:
        if query.data.startswith("menu_"):
            category = query.data.split("_")[1]
            options = {
                "hand": HAND_ACCESSORIES,
                "head": HEAD_ACCESSORIES,
                "leg": LEG_ACCESSORIES,
                "background": BACKGROUNDS,
            }.get(category, {})
            keyboard = [
                [InlineKeyboardButton(name, callback_data=f"{category}_{name}")] for name in options
            ] + [[InlineKeyboardButton("Back", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Select {category.capitalize()}:", reply_markup=reply_markup)
        elif query.data.startswith(("hand_", "head_", "leg_", "background_")):
            category, item = query.data.split("_", 1)
            user_data[user_id][category] = item
            await show_main_menu(update, context)
        elif query.data == "random":
            from random import choice
            user_data[user_id] = {
                "hand": choice(list(HAND_ACCESSORIES.keys())),
                "head": choice(list(HEAD_ACCESSORIES.keys())),
                "leg": choice(list(LEG_ACCESSORIES.keys())),
                "background": choice(list(BACKGROUNDS.keys())),
            }
            await show_main_menu(update, context)
        elif query.data == "reset":
            user_data[user_id] = {"hand": None, "head": None, "leg": None, "background": None}
            await show_main_menu(update, context)
        elif query.data == "generate":
            await generate_image(user_id, query)
    except Exception as e:
        logger.error(f"Ошибка в selection_handler: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

# Генерация изображения
async def generate_image(user_id, query):
    try:
        base_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        user_selections = user_data.get(user_id, {})

        # Добавляем фон
        background_file = BACKGROUNDS.get(user_selections.get("background"))
        if background_file:
            background = Image.open(background_file).resize(base_image.size).convert("RGBA")
            base_image = Image.alpha_composite(background, base_image)

        # Позиции и масштабы
        positions = {
            "hand": {"Phantom": ([3, 242], 0.3), "Uzi": ([15, 249], 0.4), "Cash": ([24, 269], 0.1)},
            "head": {"Stone Island": ([30, -83], 0.7), "Blunt": ([258, 252], 0.3)},
            "leg": {"Elf": ([240, 183], 0.3)},
        }

        # Добавляем аксессуары
        for category in ["hand", "head", "leg"]:
            item = user_selections.get(category)
            if item:
                file_path = HAND_ACCESSORIES.get(item) or HEAD_ACCESSORIES.get(item) or LEG_ACCESSORIES.get(item)
                position, scale = positions[category].get(item, ([0, 0], 1.0))
                if file_path:
                    accessory = Image.open(file_path).convert("RGBA")
                    accessory = accessory.resize((int(accessory.width * scale), int(accessory.height * scale)))
                    base_image.paste(accessory, position, accessory)

        # Сохраняем изображение
        output_path = f"output/result_{user_id}.png"
        base_image.save(output_path)
        await query.message.reply_photo(photo=open(output_path, "rb"))
    except Exception as e:
        logger.error(f"Ошибка при генерации изображения: {e}")
        await query.message.reply_text("Ошибка при создании изображения.")

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(selection_handler, pattern="^(menu|hand|head|leg|background|random|generate|reset)_.*"))
    application.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url=f"{APP_URL}/webhook",
    )

if __name__ == "__main__":
    main()
