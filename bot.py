import logging
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token from BotFather
BOT_TOKEN = "7913388159:AAEtF3svQ6Teo4czOccykd-P2tK-wELbbXQ"

# Mapping numbers to emojis
emoji_mapping = {
    1: "😀", 2: "😂", 3: "🥰", 4: "😎", 5: "🤩",
    6: "😇", 7: "😜", 8: "🤔", 9: "🙃", 10: "😴"
}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Send /draw to get a random number with an emoji.")

def draw(update: Update, context: CallbackContext) -> None:
    number = random.randint(1, 10)  # Generate a random number
    emoji = emoji_mapping.get(number, "❓")  # Get emoji for the number
    update.message.reply_text(f"You drew {number}: {emoji}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("draw", draw))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
