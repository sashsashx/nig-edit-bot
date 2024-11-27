from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from PIL import Image

# Store user choices
user_choices = {}

# Start command
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Coffee", callback_data='coffee')],
        [InlineKeyboardButton("KFC Wings", callback_data='kfc')],
        [InlineKeyboardButton("Reset", callback_data='reset')],
        [InlineKeyboardButton("Generate", callback_data='generate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Choose an accessory for Nig:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Choose an accessory for Nig:", reply_markup=reply_markup)

# Handle button presses
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Initialize user choices if not exists
    if user_id not in user_choices:
        user_choices[user_id] = {}

    # Process choices
    if query.data == 'coffee':
        user_choices[user_id]['accessory'] = 'coffee.png'
        await query.edit_message_text("You selected: Coffee.")
    elif query.data == 'kfc':
        user_choices[user_id]['accessory'] = 'kfc.png'
        await query.edit_message_text("You selected: KFC Wings.")
    elif query.data == 'reset':
        user_choices[user_id] = {}
        await query.edit_message_text("Selections have been reset.")
    elif query.data == 'generate':
        await query.edit_message_text("Generating image...")
        await generate_image(user_id, context, query)
        return

    # Automatically show the menu again
    await start(update, context)

# Generate the final image
async def generate_image(user_id, context, query):
    base_image = Image.open("images/nig.png")
    
    # Define accessory position (adjust as needed)
    positions = {
        'coffee.png': (60, 300),  # Adjusted coordinates for coffee (moved left by 10%)
        'kfc.png': (140, 300)    # Coordinates for KFC wings
    }

    # Get user accessory choice
    accessory_file = user_choices.get(user_id, {}).get('accessory')
    if accessory_file:
        accessory_path = f"images/{accessory_file}"
        
        # Ensure the file exists and is a PNG
        try:
            accessory = Image.open(accessory_path)
            
            # Resize the accessory (adjust size to be larger)
            accessory = accessory.resize((150, 150))  # Increased size for better proportions

            # Paste accessory onto the base image
            base_image.paste(accessory, positions[accessory_file], accessory)
        except FileNotFoundError:
            await query.message.reply_text(f"Error: {accessory_file} not found!")
            return
        except Exception as e:
            await query.message.reply_text(f"Error: {str(e)}")
            return

    # Save the generated image
    output_path = f"images/result_{user_id}.png"
    base_image.save(output_path)

    # Send the generated image to the user
    await query.message.reply_photo(photo=open(output_path, 'rb'))

# Main function to start the bot
def main():
    application = Application.builder().token("7967474690:AAE1AkydRFr-Xi-OOBRTv1pHkrrmVLYofVM").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()
