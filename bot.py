from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
import random
import logging

# Define the categories, subcategories, and their corresponding emojis
categories = {
    "Subjects": {
        "People": ["👩", "👨", "👶", "👴", "👦", "🤰"],
        "Animals": ["🐶", "🐱", "🦊", "🐻", "🐼", "🐨"],
        "Fantasy": ["🧙", "🧚", "🧛", "🧜", "🧝", "🧞"],
        "Plants": ["🌲", "🌳", "🌴", "🌵", "🌷", "🌻"],
        "Works": ["👷", "👮", "👩‍🚒", "👩‍🌾", "👩‍🍳", "👩‍🎨"]
        
    },
    "Actions": {
        "Sports": ["🏃", "🚴", "🏊", "🧘", "🍴", "💃"],
        "Music": ["🎤", "🎧", "🎷", "🎸", "🎹", "🥁"],
        "Dance": ["💃", "🕺", "👯", "🩰", "🕴️", "🩰"],
        "Emotions": ["😀", "😂", "😍", "😢", "😡", "😱"],
        "Illegal": ["🚬", "💊", "💉", "🔫", "💣", "🔪"]
    },
    "Objects": {
        "Household": ["📚", "🧹", "👖", "🕶️", "🧩", "🛴"],
        "Technology": ["💻", "📱", "🖥️", "🖨️", "📷", "🎥"],
        "Tools": ["🔧", "🔨", "🪓", "🔩", "🪛", "🧰"],
        "Clothing": ["👕", "👗", "👠", "👒", "🧣", "🧤"],
        "Food": ["🍔", "🍕", "🍣", "🍦", "🍩", "🍪"],
        "Drinks": ["🍺", "🍷", "🍸", "🍹", "🥃", "🥤"],
        "Furniture": ["🪑", "🛋️", "🛏️", "🚪", "🪟", "💺"]

    },
    "Places": {
        "Nature": ["🏡", "🏢", "🏞️", "🏖️", "🏜️", "🏕️"],
        "Buildings": ["🏠", "🏡", "🏢", "🏣", "🏤", "🏥"],
        "Transport": ["🚗", "🚕", "🚙", "🚌", "🚎", "🏎️"],
        "Public": ["🏦", "🏪", "🏫", "🏬", "🏭", "🏯"],
        "Religious": ["⛪", "🕌", "🕍", "🕋", "⛩️", "🛕"],
    },
    "Marks": {
        "Punctuation": ["❓", "❗", "‼️", "⁉️", "❣️"],
        "Stars": ["⭐", "🌟", "✨", "🔥", "💥", "💫"],
        "Weather": ["☀️", "🌤️", "⛅", "🌥️", "🌦️", "🌧️"],
        "Flags": ["🏳️", "🏴", "🏁", "🚩", "🏳️‍🌈", "🏴‍☠️"],
        "Arrows": ["➡️", "⬅️", "⬆️", "⬇️", "↗️", "↘️"],
        "Music": ["⏯️", "⏹️", "⏺️", "⏭️", "⏮️", "🔀"],
        "Special":["🔞", "🆘", "✔️", "⛔", "🚫", "❌"]
    }
}

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is input."""
    await update.message.reply_text("Welcome to the Emoji Dice Bot! Use /roll to roll the dice and create a fun story! If you struggle with options or need help, use /help.")
    
    # Notify the admin that someone is using the bot
    admin_chat_id = 'ADMIN_ID'
    user_id = update.message.from_user.id
    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"User {user_id} has started using the bot."
    )

async def button(update: Update, context: CallbackContext) -> None:
    """Callback function for inline buttons."""
    query = update.callback_query
    await query.answer()
    
    # logger.info(f"Query data: {query.data}")

    if query.data.startswith("lock_"):
        emojis = query.data.split("_")[1:]
        keyboard = [[InlineKeyboardButton(emoji, callback_data=f"locked_{i}_{emoji}") for i, emoji in enumerate(emojis)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Choose an emoji to lock:", reply_markup=reply_markup)
    elif query.data.startswith("locked_"):
        index, locked_emoji = int(query.data.split("_")[1]), query.data.split("_")[2]
        locked_emojis = context.user_data.get('locked_emojis', [])
        locked_indices = context.user_data.get('locked_indices', [])
        locked_emojis.append(locked_emoji)
        locked_indices.append(index)
        context.user_data['locked_emojis'] = locked_emojis
        context.user_data['locked_indices'] = locked_indices
        keyboard = [
            [InlineKeyboardButton("Re-roll", callback_data=f"re_roll_{'_'.join(locked_emojis)}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Locked: {locked_emoji}", reply_markup=reply_markup)
    elif query.data.startswith("re_roll_"):
        locked_emojis = query.data.split("_")[2:]
        # logger.info(f"Locked emojis for re-roll: {locked_emojis}")
        await roll(update, context, locked_emojis)

async def roll(update: Update, context: CallbackContext, locked_emojis=None) -> None:
    """Roll the dice and output emojis."""
    if locked_emojis is None:
        locked_emojis = []  

    # Retrieve locked_indices from context
    locked_indices = context.user_data.get('locked_indices', [])
    result = [None] * 6

    # Fill the result with locked emojis at their respective positions
    for index, emoji in zip(locked_indices, locked_emojis):
        result[index] = emoji

    # Collect emojis for each category in the correct order
    for i, category_name in enumerate(list(categories.keys())):
        if result[i] is None:
            for category, subcategories in categories.items():
                if category == category_name:
                    subcategory = random.choice(list(subcategories.keys()))
                    result[i] = random.choice(subcategories[subcategory])
                    break

    # Ensure no None values are in the result
    result = [emoji if emoji is not None else '' for emoji in result]

    # Remove empty strings from the result
    result = [emoji for emoji in result if emoji]

    # Ensure the result is not empty
    if not result:
        result = ["No emojis available"]

    # Create inline buttons for locking options and re-rolling
    keyboard = [
        [InlineKeyboardButton("Lock", callback_data=f"lock_{'_'.join(result)}")],
        [InlineKeyboardButton("Re-roll", callback_data=f"re_roll_{'_'.join(locked_emojis)}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the result back to the user
    if update.callback_query:
        await update.callback_query.edit_message_text(text=' '.join(result), reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=' '.join(result), reply_markup=reply_markup)

async def visualize(update: Update, context: CallbackContext) -> None:
    """Visualize every category and its subcategories."""
    result = ["Category and its subcategories:"]
    for category, subcategories in categories.items():
        result.append(f"*{category}*")
        for subcategory, emojis in subcategories.items():
            result.append(f" _{subcategory}_")
            result.append(f"    Emojis: {' '.join(emojis)}")
        result.append("")  # Add a blank line for better readability
    await update.message.reply_text("\n".join(result), parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/roll - Roll the dice and create a fun story\n"
        "/visualize - Visualize every category and its subcategories\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

async def feedback(update: Update, context: CallbackContext) -> None:
    """Start the feedback conversation."""
    await update.message.reply_text(
        "Please send your feedback. Type /cancel to stop.",
        reply_markup=ReplyKeyboardMarkup([['/cancel']], one_time_keyboard=True)
    )
    return FEEDBACK

async def receive_feedback(update: Update, context: CallbackContext) -> None:
    """Receive the feedback and send it to the admin chat."""
    user_feedback = update.message.text
    user_id = update.message.from_user.id
    admin_chat_id = 'ADMIN_ID'  
    
    # Send the feedback to the admin chat
    await context.bot.send_message(
        chat_id=admin_chat_id,
        text=f"Feedback from user {user_id}:\n{user_feedback}"
    )

    await update.message.reply_text("Thank you for your feedback!")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> None:
    """Cancel the feedback conversation"""
    await update.message.reply_text("Feedback cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Add the feedback command to the help text
async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is input."""
    help_text = (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/roll - Roll the dice and create a fun story\n"
        "/visualize - Visualize every category and its subcategories\n"
        "/feedback - Send your feedback\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_text)

FEEDBACK = range(1)

feedback_handler = ConversationHandler(
    entry_points=[CommandHandler('feedback', feedback)],
    states={
        FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("roll", roll))
    application.add_handler(CommandHandler("visualize", visualize))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(feedback_handler)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
