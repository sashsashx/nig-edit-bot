import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image

# Store user choices
user_choices = {}

# Define available accessories for each part of the body
ACCESSORIES = {
    "hand": {"coffee": "Coffee", "kfc": "KFC Wings"},
    "head": {"maga_hat": "MAGA Hat", "wif_hat": "WIF Hat", "chrome_hat": "Chrome Hat"},
    "torso": {},  # Empty for now
    "legs": {},   # Empty for now
}

# Start command
async def start(update: Update, context):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Build the main menu
    keyboard = [
        [
            InlineKeyboardButton(
                f"Hand [{user_choices.get(user_id, {}).get('hand', 'None')}]",
                callback_data="menu_hand",
            )
        ],
        [
            InlineKeyboardButton(
                f"Head [{user_choices.get(user_id, {}).get('head', 'None')}]",
                callback_data="menu_head",
            )
        ],
        [
            InlineKeyboardButton(f"Torso [None]", callback_data="menu_torso"),
            InlineKeyboardButton(f"Legs [None]", callback_data="menu_legs"),
        ],
        [InlineKeyboardButton("Reset", callback_data="reset")],
        [InlineKeyboardButton("Generate", callback_data="generate")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send or edit message
    if update.message:
        await update.message.reply_text("Choose a body part:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "Choose a body part:", reply_markup=reply_markup
        )

# Menu for a specific body part
async def menu(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    part = query.data.split("_")[1]

    # Build the menu for the specific body part
    accessories = ACCESSORIES.get(part, {})
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"select_{part}_{key}")]
        for key, name in accessories.items()
    ]
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(f"Choose an accessory for {part.capitalize()}:", reply_markup=reply_markup)

# Handle accessory selection
async def select(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        _, part, accessory = query.data.split("_")
    except ValueError:
        await query.answer("Invalid selection!")
        return

    # Save the selected accessory
    if user_id not in user_choices:
        user_choices[user_id] = {}
    user_choices[user_id][part] = ACCESSORIES[part][accessory]

    # Return to main menu
    await start(update, context)

# Reset all selections
async def reset(update: Update, context):
    user_id = update.callback_query.from_user.id
    user_choices[user_id] = {}
    await start(update, context)

# Generate the final image
async def generate(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id

    # Open base image
    base_image = Image.open("images/nig.png")
    
    # Define accessory positions
    positions = {
        "hand": (60, 300),              # Left hand
        "head": (175, 50),             # Centered at the top 20% for head
        # Add positions for torso and legs later
    }

    # Add accessories to the image
    for part, accessory in user_choices.get(user_id, {}).items():
        if accessory:
            accessory_image = Image.open(f"images/{part}/{accessory}.png").resize((150, 150))
            base_image.paste(accessory_image, positions[part], accessory_image)

    # Save and send the image
    output_path = f"images/result_{user_id}.png"
    base_image.save(output_path)
    await query.message.reply_photo(photo=open(output_path, "rb"))

# Main function to start the bot
def main():
    application = Application.builder().token("7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu, pattern="menu_"))
    application.add_handler(CallbackQueryHandler(select, pattern="select_"))
    application.add_handler(CallbackQueryHandler(reset, pattern="reset"))
    application.add_handler(CallbackQueryHandler(generate, pattern="generate"))
    application.add_handler(CallbackQueryHandler(start, pattern="main_menu"))

    # Webhook configuration
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook"
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    main()
