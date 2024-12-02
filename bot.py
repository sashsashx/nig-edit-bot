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

# Координаты и масштаб
POSITIONS = {
    "hand": {
        "Coffee": {"position": (-45, 208), "scale": 0.5},
        "KFC": {"position": (0, 221), "scale": 0.3},
        "Uzi": {"position": (15, 249), "scale": 0.4},
        "Cash": {"position": (24, 269), "scale": 0.1},
        "Phantom": {"position": (3, 242), "scale": 0.3},
        "US Flag": {"position": (-22, 137), "scale": 0.2},
    },
    "head": {
        "Maga Hat": {"position": (0, -15), "scale": 0.5},
        "WIF Hat": {"position": (45, -43), "scale": 0.7},
        "Chrome Hat": {"position": (70, -29), "scale": 0.3},
        "Stone Island": {"position": (30, -83), "scale": 0.7},
        "Blunt": {"position": (258, 252), "scale": 0.3},
        "Glasses": {"position": (92, 120), "scale": 0.3},
        "BK Crown": {"position": (123, -13), "scale": 0.2},
    },
    "leg": {
        "Elf": {"position": (240, 183), "scale": 0.3},
        "Skate": {"position": (19, 225), "scale": 0.9},
    },
}

# Функция генерации изображения
async def generate_image(user_id, query):
    try:
        logger.info(f"Начинаем генерацию изображения для пользователя {user_id}")
        base_image = Image.open(BASE_IMAGE_PATH).convert("RGBA")
        logger.info("Базовое изображение загружено.")
        selections = user_data[user_id]
        for category in ["hand", "head", "leg"]:
            if selections[category]:
                accessory_path = HAND_ACCESSORIES[selections[category]]
                logger.info(f"Добавляем аксессуар: {accessory_path}")
                accessory = Image.open(accessory_path).convert("RGBA")
                pos = POSITIONS[category][selections[category]]["position"]
                scale = POSITIONS[category][selections[category]]["scale"]
                accessory = accessory.resize(
                    (int(accessory.width * scale), int(accessory.height * scale)),
                    Image.Resampling.LANCZOS,
                )
                base_image.paste(accessory, pos, accessory)

        if selections["background"]:
            background_path = BACKGROUNDS[selections["background"]]
            logger.info(f"Добавляем фон: {background_path}")
            background = Image.open(background_path).convert("RGBA")
            base_image = Image.alpha_composite(background, base_image)

        output_path = f"output/result_{user_id}.png"
        base_image.save(output_path)
        await query.message.reply_photo(photo=open(output_path, "rb"))
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        await query.message.reply_text("Ошибка при генерации изображения. Убедитесь, что все элементы выбраны.")

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
