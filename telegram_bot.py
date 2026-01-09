import os
import telebot
import json
import time
from telebot import types
from cryptography.fernet import Fernet
from uuid import uuid4

# --- 1. TOKEN DE ACCESO ---
TOKEN = "8278562008:AAHo2mi6CMBq8fdzpqtZqINZCsJHk72vHRE"
BOT_USERNAME = "@dec26visionbot"

# --- 2. JEFAZOS (Dueños del Sistema) ---
DEV_ID = 1791529545  # ID Desarrollador
OWNER_ID = 6507236702  # ID Dueña

SUPER_ADMINS = [DEV_ID, OWNER_ID]

bot = telebot.TeleBot(TOKEN)
KEY_FILE = 'vault.key'
DB_FILE = 'staff_db.json'

# --- 3. LÓGICA DE SEGURIDAD ---


def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key


def get_staff_db():
    if not os.path.exists(DB_FILE):
        save_staff_db([])
        return []
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return []


def save_staff_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)


def can_lock(user_id):
    staff = get_staff_db()
    return user_id in SUPER_ADMINS or user_id in staff


def is_boss(user_id):
    return user_id in SUPER_ADMINS


cipher = Fernet(load_or_create_key())

# --- 4. INTERFAZ GRÁFICA ---


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_id = types.InlineKeyboardButton("🆔 ID", callback_data='myid')
    btn_help = types.InlineKeyboardButton("📜 Help", callback_data='help')
    markup.add(btn_id, btn_help)
    return markup


@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id

    # 1. Definir rol estético
    role_status = "𝚄𝚜𝚎𝚛 𝙵𝚛𝚎𝚎"
    show_admin_commands = False

    if can_lock(user_id):
        role_status = "𝚂𝚝𝚊𝚏𝚏 / 𝙰𝚐𝚎𝚗𝚝"
        show_admin_commands = True

    if is_boss(user_id):
        role_status = "𝙾𝚠𝚗𝚎𝚛 / 𝙰𝚍𝚖𝚒𝚗"
        show_admin_commands = True

    # 2. Diseño del mensaje
    text = ("✨ 𝐃𝐄𝐂𝐎𝐃𝐄𝐑 𝐕𝐈𝐒𝐈𝐎𝐍 𝐁𝐍𝐙 ✨\n\n"
            f"➤ 𝐒𝐭𝐚𝐭𝐮𝐬: {role_status}\n"
            "-----------------------\n"
            "𝐂𝐨𝐦𝐚𝐧𝐝𝐨𝐬 𝐃𝐞 𝐋𝐞𝐜𝐭𝐮𝐫𝐚:\n\n"
            "➤ /read - 𝙳𝚎𝚜𝚎𝚗𝚌𝚛𝚒𝚙𝚝𝚊𝚛 𝚌𝚘𝚗𝚝𝚎𝚗𝚒𝚍𝚘.\n"
            "➤ /myid - 𝚅𝚎𝚛 𝚝𝚞 𝙸𝙳 𝚙𝚊𝚛𝚊 𝚜𝚘𝚕𝚒𝚌𝚒𝚝𝚊𝚛 𝚊𝚌𝚌𝚎𝚜𝚘.")

    # 3. Añadir secciones extra SOLO si es Staff/Dueño
    if show_admin_commands:
        text += ("\n\n𝐇𝐞𝐫𝐫𝐚𝐦𝐢𝐞𝐧𝐭𝐚𝐬 𝐒𝐭𝐚𝐟𝐟:\n\n"
                 "➤ /lock - 𝙴𝚗𝚌𝚛𝚒𝚙𝚝𝚊𝚛 (𝙼𝚊𝚗𝚞𝚊𝚕).\n"
                 f"➤ `{BOT_USERNAME} ...` - 𝙴𝚗𝚌𝚛𝚒𝚙𝚝𝚊𝚛 (𝙼𝚘𝚍𝚘 𝙸𝚗𝚕𝚒𝚗𝚎).")

    # 4. Sección de administración
    if is_boss(user_id):
        text += ("\n\n𝐀𝐝𝐦𝐢𝐧𝐢𝐬𝐭𝐫𝐚𝐜𝐢ó𝐧:\n\n"
                 "➤ /promote - 𝙳𝚊𝚛 𝚛𝚊𝚗𝚐𝚘.\n"
                 "➤ /fire - 𝚀𝚞𝚒𝚝𝚊𝚛 𝚛𝚊𝚗𝚐𝚘.")

    bot.reply_to(message,
                 text,
                 reply_markup=main_menu(),
                 parse_mode='Markdown')


# --- 5. MODO INLINE (CODE) ---
@bot.inline_handler(lambda query: len(query.query) > 0)
def query_text(inline_query):
    text = inline_query.query.strip()
    user_id = inline_query.from_user.id
    results = []

    # Seguridad: Solo Staff
    if can_lock(user_id):
        try:
            encrypted_hash = cipher.encrypt(text.encode()).decode()

            input_content = types.InputTextMessageContent(
                f"✨ **𝐕𝐈𝐒𝐈𝐎𝐍 𝐁𝐍𝐙 𝐒𝐄𝐂𝐔𝐑𝐄** ✨\n\n➤ 𝘾𝙊𝘿𝙀:\n`{encrypted_hash}`\n\n👇 _Usa el bot para decodificar_",
                parse_mode='Markdown')

            item_lock = types.InlineQueryResultArticle(
                id=str(uuid4()),
                title="🔒 Secure Lock",
                description="Generar Token",
                input_message_content=input_content,
                thumb_url="https://img.icons8.com/color/48/lock-landscape.png")
            results.append(item_lock)
        except:
            pass

    # Guest ID (Para todos)
    if text.lower() == 'myid':
        item_id = types.InlineQueryResultArticle(
            id=str(uuid4()),
            title="🆔 Mi ID",
            description=str(user_id),
            input_message_content=types.InputTextMessageContent(
                f"🆔 Mi ID es: `{user_id}`", parse_mode='Markdown'))
        results.append(item_id)

    if results:
        bot.answer_inline_query(inline_query.id, results, cache_time=1)


# --- 6. COMANDOS ADMIN ---


@bot.message_handler(commands=['promote'])
def add_admin(message):
    if not is_boss(message.from_user.id): return
    try:
        new_id = int(message.text.split()[1])
        staff = get_staff_db()
        if new_id not in staff:
            staff.append(new_id)
            save_staff_db(staff)
            bot.reply_to(message,
                         f"✅ ID `{new_id}` -> 𝚂𝚝𝚊𝚏𝚏.",
                         parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ Ya es Staff.")
    except:
        pass


@bot.message_handler(commands=['fire'])
def remove_admin(message):
    if not is_boss(message.from_user.id): return
    try:
        target = int(message.text.split()[1])
        staff = get_staff_db()
        if target in staff:
            staff.remove(target)
            save_staff_db(staff)
            bot.reply_to(message,
                         f"⛔ ID `{target}` eliminado.",
                         parse_mode='Markdown')
    except:
        pass


# --- 7. COMANDOS FUNCIONALES ---


@bot.message_handler(commands=['lock'])
def manual_lock(message):
    if not can_lock(message.from_user.id): return
    try:
        data = message.text[len('/lock '):].strip()
        if not data: return
        token = cipher.encrypt(data.encode()).decode()
        # Etiqueta: CODE
        bot.reply_to(message, f"➤ 𝘾𝙊𝘿𝙀:\n`{token}`", parse_mode='Markdown')
    except:
        pass


@bot.message_handler(commands=['read'])
def manual_read(message):
    try:
        token = message.text[len('/read '):].strip()
        if not token:
            bot.reply_to(message, "⚠️ 𝙴𝚗𝚟𝚒𝚊 𝚎𝚕 𝙷𝚊𝚜𝚑.", parse_mode='Markdown')
            return
        decoded = cipher.decrypt(token.encode()).decode()

        # Etiqueta: DESCIFRADO (Corregido con S)
        bot.reply_to(message,
                     f"➤ 𝘿𝙀𝙎𝘾𝙄𝙁𝙍𝘼𝘿𝙊:\n`{decoded}`",
                     parse_mode='Markdown')
    except:
        bot.reply_to(message, "❌ 𝙷𝚊𝚜𝚑 𝙸𝚗𝚟𝚊𝚕𝚒𝚍𝚘", parse_mode='Markdown')


@bot.message_handler(commands=['myid'])
def show_my_id(message):
    bot.reply_to(message,
                 f"🆔 ID: `{message.from_user.id}`",
                 parse_mode='Markdown')


# --- 8. CALLBACKS ---


@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    if call.data == 'myid':
        bot.answer_callback_query(call.id,
                                  f"ID: {call.from_user.id}",
                                  show_alert=True)
    elif call.data == 'help':
        t = "🔐 Guest: Solo /read\n🔓 Staff: Puede usar /lock"
        bot.answer_callback_query(call.id, t, show_alert=True)


# --- 9. EJECUCIÓN ---

if __name__ == "__main__":
    print(f"✨ INICIANDO {BOT_USERNAME} - DECODER VISION ✨")
    try:
        bot.delete_webhook()
    except:
        pass

    cmd_list = [
        types.BotCommand("start", "Inicio"),
        types.BotCommand("read", "🔓 Desencriptar"),
        types.BotCommand("myid", "🆔 Ver ID"),
    ]
    bot.set_my_commands(cmd_list)

    while True:
        try:
            bot.infinity_polling(timeout=25, long_polling_timeout=10)
        except Exception as e:
            time.sleep(3)
