import os
import logging
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Check if token exists
if not TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")
    sys.exit(1)

logger.info("✅ Bot token loaded successfully")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    
    welcome_text = f"""
🚀 Welcome to SBR24H Crypto Bot, {user.first_name}!

I'm your crypto companion for 24/7 market insights.

🔹 *Available Commands:*
/price - Check crypto prices
/help - Show all commands

🛡️ *Security Notice:*
I will NEVER ask for your private keys or seed phrases!
"""
    
    keyboard = [
        [InlineKeyboardButton("💰 Price", callback_data='price')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = """
📖 *Available Commands:*

/start - Start the bot
/help - Show this help message
/price - Get cryptocurrency prices
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch cryptocurrency prices."""
    await update.message.reply_text(
        "💰 *Current Crypto Prices*\n\n"
        "BTC: $67,432.00 📈 (+2.3%)\n"
        "ETH: $3,456.00 📈 (+1.5%)\n"
        "SOL: $145.00 📉 (-0.8%)\n\n"
        "🔄 Real prices coming soon!",
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'price':
        await price_command(update, context)
    elif data == 'help':
        await help_command(update, context)

def main():
    """Start the bot."""
    logger.info("🚀 Starting SBR24H Crypto Bot...")
    
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("price", price_command))
        
        # Add callback handler for buttons
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Start the bot
        logger.info("🤖 Bot is running and polling for updates...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
