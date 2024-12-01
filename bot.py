import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Define accessory data
ACCESSORY_CATEGORIES = {
    "hand": ["uzi.png", "cash.png", "phantom.png", "US_flag.png"],
    "head": ["chrome_hat.png", "maga_hat.png", "wif_hat.png", "stone_island.png", "blunt.png", "glasses.png", "BK_crown.png"],
    "leg": ["elf.png"],
    "background": ["matrix.png", "mario.png", "windows.png", "strip.png", "MLK.png"]
}

# User choices
user_choices = {}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}

    keyboard = [
        [InlineKeyboardButton("Hand", callback_data="menu_hand")],
        [InlineKeyboardButton("Head", callback_data="menu_head")],
        [InlineKeyboardButton("Leg", callback_data="menu_leg")],
        [InlineKeyboardButton("Background", callback_data="menu_background")],
        [InlineKeyboardButton("Random", callback_data="random")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
        [InlineKeyboardButton("Reset", callback_data="reset")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Customize your image:", reply_markup=reply_markup)

# Menu selection handler
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Generate category menu
    category = query.data.split("_")[1]
    if category not in ACCESSORY_CATEGORIES:
        await query.edit_message_text("Invalid category selected.")
        return

    buttons = [
        [InlineKeyboardButton(item.split(".")[0].replace("_", " ").capitalize(), callback_data=f"{category}_{item}")]
        for item in ACCESSORY_CATEGORIES[category]
    ]
    buttons.append([InlineKeyboardButton("Back to Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(f"Choose an item for {category.capitalize()}:", reply_markup=reply_markup)

# Selection handler
async def selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    # Parse the selection
    try:
        category, item = query.data.split("_")
    except ValueError:
        await query.edit_message_text("Invalid selection. Please try again.")
        return

    if category in ACCESSORY_CATEGORIES and item in ACCESSORY_CATEGORIES[category]:
        user_choices[user_id][category] = item
        await query.edit_message_text(f"You selected: {item.split('.')[0].capitalize()}. Returning to main menu...")
        await start(update, context)
    else:
        await query.edit_message_text("Invalid selection. Please try again.")

# Random selection handler
async def random_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    await update.callback_query.answer()

    # Randomly assign an accessory from each category
    user_choices[user_id] = {
        category: random.choice(items) for category, items in ACCESSORY_CATEGORIES.items()
    }

    await update.callback_query.edit_message_text("Random selections made! Returning to main menu...")
    await start(update, context)

# Generate image handler
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer("Generating image...")

    # Process and generate the image (mock example here)
    selections = user_choices.get(user_id, {})
    output_text = "Generating image with the following selections:\n"
    for category, item in selections.items():
        output_text += f"{category.capitalize()}: {item or 'None'}\n"

    await query.edit_message_text(output_text)

# Reset handler
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    user_choices[user_id] = {"hand": None, "head": None, "leg": None, "background": None}

    await update.callback_query.answer("Selections reset.")
    await start(update, context)

# Main function to start the bot
def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    APP_URL = os.getenv("APP_URL")

    if not BOT_TOKEN or not APP_URL:
        raise ValueError("BOT_TOKEN and APP_URL environment variables must be set.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(selection_handler, pattern="^(hand|head|leg|background)_.+"))
    application.add_handler(CallbackQueryHandler(random_selection, pattern="^random$"))
    application.add_handler(CallbackQueryHandler(generate_image, pattern="^generate$"))
    application.add_handler(CallbackQueryHandler(reset, pattern="^reset$"))

    # Run webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=443,
        url_path=BOT_TOKEN,
        webhook_url=f"{APP_URL}/{BOT_TOKEN}",
    )

if __name__ == "__main__":
    main()
