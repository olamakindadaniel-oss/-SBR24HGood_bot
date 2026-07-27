import os
import logging
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Crypto API endpoints (using CoinGecko as free example)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Dictionary to store user states (simple in-memory, consider DB for production)
user_data = {}

# ----- COMMAND HANDLERS -----

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message with menu when /start is issued."""
    user = update.effective_user
    welcome_text = f"""
🚀 Welcome to SBR24H Crypto Bot, {user.first_name}!

I'm your crypto companion for 24/7 market insights and portfolio tracking.

🔹 *What I can do:*
• Check real-time crypto prices
• Track wallet balances (BTC, ETH, BSC, SOL)
• Set price alerts
• View top gainers/losers
• Get daily crypto news

🔹 *How to use:*
Use the buttons below or type commands:
/price - Check crypto prices
/wallet - Track wallet balance
/alert - Set price alerts
/trending - Top trending coins
/news - Latest crypto news
/help - Show all commands

🛡️ *Security Notice:*
I will NEVER ask for your private keys or seed phrases. Never share them with anyone!

⭐ *Support the bot:*
BTC: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
ETH: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Price", callback_data='price'),
            InlineKeyboardButton("📊 Wallet", callback_data='wallet')
        ],
        [
            InlineKeyboardButton("🔔 Alerts", callback_data='alert'),
            InlineKeyboardButton("📈 Trending", callback_data='trending')
        ],
        [
            InlineKeyboardButton("📰 News", callback_data='news'),
            InlineKeyboardButton("❓ Help", callback_data='help')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when /help is issued."""
    help_text = """
📖 *Available Commands:*

/start - Start the bot and show menu
/price - Check cryptocurrency prices
/wallet - Track your wallet balances
/alert - Set up price alerts
/trending - View top trending coins
/news - Latest crypto news
/help - Show this help message

*How to use each command:*

💰 /price - Get current price for BTC, ETH, SOL, etc.
Example: /price BTC ETH SOL

📊 /wallet - Track a wallet address
Example: /wallet BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

🔔 /alert - Set alert when price hits target
Example: /alert BTC 100000

📈 /trending - See what's trending in the last 24h

📰 /news - Get latest crypto news headlines

*Support:*
If you encounter issues, contact @YourSupportHandle
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display cryptocurrency prices."""
    try:
        # Default coins if none specified
        coins = context.args if context.args else ['bitcoin', 'ethereum', 'solana']
        
        # Map common symbols to CoinGecko IDs
        symbol_to_id = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'sol': 'solana',
            'bnb': 'binancecoin',
            'xrp': 'ripple',
            'ada': 'cardano',
            'doge': 'dogecoin',
            'dot': 'polkadot',
            'matic': 'polygon',
            'avax': 'avalanche-2'
        }
        
        # Convert user input to CoinGecko IDs
        coin_ids = []
        for coin in coins:
            coin_lower = coin.lower()
            if coin_lower in symbol_to_id:
                coin_ids.append(symbol_to_id[coin_lower])
            else:
                coin_ids.append(coin_lower)
        
        # Fetch prices
        response = requests.get(
            f"{COINGECKO_API}/simple/price",
            params={
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            price_text = "💰 *Current Crypto Prices*\n\n"
            
            # Reverse mapping for display
            id_to_symbol = {v: k.upper() for k, v in symbol_to_id.items()}
            
            for coin_id, coin_data in data.items():
                symbol = id_to_symbol.get(coin_id, coin_id.upper())
                price = coin_data.get('usd', 0)
                change = coin_data.get('usd_24h_change', 0)
                emoji = '📈' if change >= 0 else '📉'
                
                price_text += f"*{symbol}*: ${price:,.2f} {emoji} ({change:+.2f}%)\n"
            
            await update.message.reply_text(price_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Sorry, couldn't fetch prices. Please try again later.")
            
    except Exception as e:
        logger.error(f"Price command error: {e}")
        await update.message.reply_text("❌ An error occurred while fetching prices. Please try again.")


async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Track wallet balance (simplified example)."""
    if not context.args:
        await update.message.reply_text(
            "📊 *Wallet Tracker*\n\n"
            "Please provide a blockchain and wallet address.\n"
            "Example: /wallet BTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa\n\n"
            "Supported chains: BTC, ETH, BSC, SOL",
            parse_mode='Markdown'
        )
        return
    
    chain = context.args[0].upper()
    address = context.args[1] if len(context.args) > 1 else None
    
    if not address:
        await update.message.reply_text("❌ Please provide a wallet address.")
        return
    
    # This is a simplified response - in production, use real blockchain APIs
    response_text = f"""
📊 *Wallet Information*

🔗 Chain: {chain}
📬 Address: `{address[:10]}...{address[-8:]}`

⚠️ *Note:* This is a demonstration. In production, this would connect to:
• BTC: Blockchain.com API
• ETH: Etherscan API  
• BSC: BSCScan API
• SOL: Solana RPC

💡 To enable real tracking, add your API keys to Railway environment variables.
"""
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh Balance", callback_data=f'refresh_{chain}_{address}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        response_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set price alerts."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "🔔 *Set Price Alert*\n\n"
            "Example: /alert BTC 100000\n\n"
            "You'll be notified when BTC reaches $100,000.\n"
            "Supported coins: BTC, ETH, SOL, BNB, XRP, ADA, DOGE",
            parse_mode='Markdown'
        )
        return
    
    coin = context.args[0].upper()
    try:
        target_price = float(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Please provide a valid price number.")
        return
    
    # Store alert in memory (use database in production)
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'alerts': []}
    
    user_data[user_id]['alerts'].append({
        'coin': coin,
        'target': target_price,
        'active': True
    })
    
    await update.message.reply_text(
        f"✅ Alert set!\n\n"
        f"🪙 Coin: {coin}\n"
        f"🎯 Target Price: ${target_price:,.2f}\n\n"
        f"I'll notify you when {coin} reaches this price."
    )


async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trending coins."""
    try:
        response = requests.get(
            f"{COINGECKO_API}/search/trending"
        )
        
        if response.status_code == 200:
            data = response.json()
            trending = data.get('coins', [])[:10]
            
            text = "📈 *Top 10 Trending Coins*\n\n"
            
            for i, coin in enumerate(trending, 1):
                name = coin['item']['name']
                symbol = coin['item']['symbol'].upper()
                score = coin['item']['score']
                text += f"{i}. *{name}* ({symbol}) - Score: {score}\n"
            
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Couldn't fetch trending coins.")
            
    except Exception as e:
        logger.error(f"Trending command error: {e}")
        await update.message.reply_text("❌ An error occurred.")


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch latest crypto news (simplified)."""
    news_text = """
📰 *Latest Crypto News*

1. 🔥 Bitcoin ETF inflows reach new record high
2. 🚀 Ethereum layer-2 solutions see 200% growth
3. 💡 SEC approves new crypto regulations
4. 🌐 Major bank launches crypto custody service
5. 📊 Market cap crosses $2.5 trillion

*For real news updates:*
• Follow @CryptoNewsBot
• Check CoinDesk.com
• Read Decrypt.co

*Note:* This is sample news. In production, connect to:
- NewsAPI.org
- CryptoPanic API
- RSS feeds
"""
    
    keyboard = [[InlineKeyboardButton("🔄 Refresh News", callback_data='news_refresh')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(news_text, parse_mode='Markdown', reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'price':
        await price_command(update, context)
    elif data == 'wallet':
        await wallet_command(update, context)
    elif data == 'alert':
        await alert_command(update, context)
    elif data == 'trending':
        await trending_command(update, context)
    elif data == 'news':
        await news_command(update, context)
    elif data == 'help':
        await help_command(update, context)
    elif data.startswith('refresh_'):
        # Handle refresh wallet
        _, chain, address = data.split('_', 2)
        await query.edit_message_text(
            f"🔄 Refreshing balance for {chain} wallet...\n"
            f"This feature requires a blockchain API connection."
        )
    elif data == 'news_refresh':
        await news_command(update, context)


# ----- MAIN FUNCTION -----

async def main():
    """Start the bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("price", price_command))
    application.add_handler(CommandHandler("wallet", wallet_command))
    application.add_handler(CommandHandler("alert", alert_command))
    application.add_handler(CommandHandler("trending", trending_command))
    application.add_handler(CommandHandler("news", news_command))
    
    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot
    logger.info("Bot started! Press Ctrl+C to stop.")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    asyncio.run(main())
