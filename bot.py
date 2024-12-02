import logging
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к базовому изображению
BASE_IMAGE_PATH = "images/base.png"

# Данные аксессуаров
HAND_ACCESSORIES = {
    "Coffee": {"path": "images/hand/coffee.png", "position": (-45, 208), "scale": 0.5},
    "KFC": {"path": "images/hand/kfc.png", "position": (0, 221), "scale": 0.3},
    "Uzi": {"path": "images/hand/uzi.png", "position": (15, 249), "scale": 0.4},
    "Cash": {"path": "images/hand/cash.png", "position": (24, 269), "scale": 0.1},
    "Phantom": {"path": "images/hand/phantom.png", "position": (3, 242), "scale": 0.3},
    "US Flag": {"path": "images/hand/US_flag.png", "position": (-22, 137), "scale": 0.2},
}

HEAD_ACCESSORIES = {
    "Maga Hat": {"path": "images/head/maga_hat.png", "position": (0, -15), "scale": 0.5},
    "WIF Hat": {"path": "images/head/wif_hat.png", "position": (45, -43), "scale": 0.7},
    "Chrome Hat": {"path": "images/head/chrome_hat.png", "position": (70, -29), "scale": 0.3},
    "Stone Island": {"path": "images/head/stone_island.png", "position": (30, -83), "scale": 0.7},
    "Blunt": {"path": "images/head/blunt.png", "position": (258, 252), "scale": 0.3},
    "Glasses": {"path": "images/head/glasses.png", "position": (92, 120), "scale": 0.3},
    "BK Crown": {"path": "images/head/BK_crown.png", "position": (123, -13), "scale": 0.2},
}

LEG_ACCESSORIES = {
    "Elf": {"path": "images/leg/elf.png", "position": (240, 183), "scale": 0.3},
    "Skate": {"path": "images/leg/skate.png", "position": (19, 225), "scale": 0.9},
}

# Данные пользователей
user_data = {}

# Функция старта
async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_data[user_id] = {"hand": None, "head": None, "leg": None}
    await show_main_menu(update, context)

# Главное меню
async def show_main_menu(update: Update, context):
    user_id = update.effective_user.id
    selections = user_data.get(user_id, {"hand": None, "head": None, "leg": None})
    keyboard = [
        [
            InlineKeyboardButton(f"Hand: {selections['hand'] or 'None'}", callback_data="hand"),
            InlineKeyboardButton(f"Head: {selections['head'] or 'None'}", callback_data="head"),
            InlineKeyboardButton(f"Leg: {selections['leg'] or 'None'}", callback_data="leg"),
        ],
        [InlineKeyboardButton("Generate", callback_data="generate"), InlineKeyboardButton("Reset", callback_data="reset")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Customize your character:", reply_markup=markup)

# Выбор категории
async def category_handler(update: Update, context):
    query = update.callback_query
    category = query.data
    query.answer()
    accessories = (
        HAND_ACCESSORIES if category == "hand" else HEAD_ACCESSORIES if category == "head" else LEG_ACCESSORIES
    )
    keyboard = [[InlineKeyboardButton(item, callback_data=f"{category}:{item}")] for item in accessories]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Select an accessory for {category}:", reply_markup=markup)

# Обработчик выбора аксессуаров
async def accessory_handler(update: Update, context):
    query = update.callback_query
    category, selection = query.data.split(":")
    user_id = query.from_user.id
    user_data[user_id][category] = selection
    await show_main_menu(update, context)

# Генерация изображения
async def generate_image(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    try:
        base_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        selections = user_data[user_id]
        for category, items in [
            ("hand", HAND_ACCESSORIES),
            ("head", HEAD_ACCESSORIES),
            ("leg", LEG_ACCESSORIES),
        ]:
            if selections[category]:
                accessory_data = items[selections[category]]
                accessory_image = Image.open(accessory_data["path"]).convert("RGBA")
                position = accessory_data["position"]
                scale = accessory_data["scale"]
                accessory_image = accessory_image.resize(
                    (int(accessory_image.width * scale), int(accessory_image.height * scale)), Image.ANTIALIAS
                )
                base_image.paste(accessory_image, position, accessory_image)
        output_path = f"output/result_{user_id}.png"
        base_image.save(output_path)
        await query.message.reply_photo(photo=open(output_path, "rb"))
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        await query.message.reply_text("Error generating the image. Try again.")

# Сброс данных
async def reset_handler(update: Update, context):
    user_id = update.callback_query.from_user.id
    user_data[user_id] = {"hand": None, "head": None, "leg": None}
    await show_main_menu(update, context)

# Роутинг
app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(category_handler, pattern="^(hand|head|leg)$"))
app.add_handler(CallbackQueryHandler(accessory_handler, pattern="^(hand|head|leg):"))
app.add_handler(CallbackQueryHandler(generate_image, pattern="^generate$"))
app.add_handler(CallbackQueryHandler(reset_handler, pattern="^reset$"))

if __name__ == "__main__":
    logger.info("Bot is running...")
    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="webhook",
        webhook_url="YOUR_WEBHOOK_URL",
    )
