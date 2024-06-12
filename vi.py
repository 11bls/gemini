import requests
import time
import sqlite3
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up your bot token and owner ID here
BOT_TOKEN = '6552075227:AAECRZ4bBHmzpWlyKuVCKxDhFbpQvneK7Yc'
OWNER_ID = '6070918315'

# ASCII Art and intro message
G = '\033[1;30;40m'
Y = '\033[92m'
K = '\033[91m'
M = '\033[94m'
S = '\033[93m'
P = '\033[95m'
intro_message = G + '''⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣷⣦⣄        
⠀⠀⣀⣤⣶⣶⣦⣄⠀⠈⣿⣿⣿⣿⡆            
⠶⣿⣿⣿⣿⣿⣿⣿⣿⣦⣿⣿⣿⣿⣷                 
⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣄                      
⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣀⣤⣤⣤⡤              
⠀⠀⢀⣠⣤⣼⣿⣿⣿⣿⣿⣿⣿⡿⣿⣿⣿⣿⣿⣿⣿⣥⣤⣤              
⠐⠺⠿⢿⣿⣿⣿⣿⣿⡏⢸⡿⠋⠀⣼⠏⣿⣿⣿⣿⡿⠟⠉
⠀⠀⠀⠀⢈⣽⣿⣇⠀⠁⠈⠀⠀⠀⠁⠀⠉⣿⣿⣷⠶⠄                 
⠀⠀⠀⠀⠉⠉⠉⠉⠳⡀⠀⠀⠀⠀⠀⣠⠾⠟⠂             
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⣄⣀⡠⠞⠁'''

# Define the function to call the Gemini API
def gemini_api(message):
    url = "https://dev-the-dark-lord.pantheonsite.io/wp-admin/js/Apis/Gemini.php"
    params = {"message": message}
    response = requests.get(url, params=params)
    return response.text

# Initialize the SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
conn.commit()

# Handle incoming messages
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = gemini_api(user_message)
    update.message.reply_text(response)

# Handle the /reklam command
def reklam_command(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == int(OWNER_ID):
        channel_link = ' '.join(context.args)
        if channel_link:
            c.execute("SELECT id FROM users")
            users = c.fetchall()
            for user_id in users:
                if user_id[0] != int(OWNER_ID):
                    try:
                        context.bot.send_message(chat_id=user_id[0], text="Reklam kanalı: " + channel_link)
                    except Exception as e:
                        print(f"Could not send message to {user_id[0]}: {e}")
            update.message.reply_text("Reklam gönderildi!")
        else:
            update.message.reply_text("Lütfen geçerli bir kanal linki girin.")
    else:
        update.message.reply_text("Bu komutu kullanma yetkiniz yok.")

# Handle the /setimage command to save the image
def set_image(update: Update, context: CallbackContext) -> None:
    if update.message.from_user.id == int(OWNER_ID):
        if update.message.photo:
            photo_file = update.message.photo[-1].get_file()
            file_path = photo_file.download()
            c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('start_image', ?)", (file_path,))
            conn.commit()
            update.message.reply_text("Resim başarıyla kaydedildi!")
        else:
            update.message.reply_text("Lütfen bir resim gönderin.")
    else:
        update.message.reply_text("Bu komutu kullanma yetkiniz yok.")

# Handle new user registration
def register_user(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()

# Handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    c.execute("SELECT value FROM settings WHERE key = 'start_image'")
    result = c.fetchone()
    if result:
        start_image_path = result[0]
        update.message.reply_photo(photo=open(start_image_path, 'rb'))
    update.message.reply_text("Merhaba! Benimle konuşarak sorularınızı sorabilirsiniz. Yapımcım @zirvebenimyerim")

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reklam", reklam_command))
    dispatcher.add_handler(CommandHandler("setimage", set_image))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, register_user))
    dispatcher.add_handler(MessageHandler(Filters.photo & Filters.user(user_id=int(OWNER_ID)), set_image))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print(intro_message)
    main()