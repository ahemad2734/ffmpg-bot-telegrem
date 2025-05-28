import telebot
import subprocess
import threading

TOKEN = 'PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)

user_data = {}
ffmpeg_process = None
lock = threading.Lock()

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "مرحباً! صيفط لي رابط البث RTMP (بدون s):")
    user_data[chat_id] = {}

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global ffmpeg_process
    with lock:
        if ffmpeg_process:
            ffmpeg_process.terminate()
            ffmpeg_process = None
            bot.send_message(message.chat.id, "تم إيقاف البث.")
        else:
            bot.send_message(message.chat.id, "ما كاينش بث شغال.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global ffmpeg_process
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        bot.send_message(chat_id, "بدا بالمير /start أولاً.")
        return

    if 'rtmp' not in user_data[chat_id]:
        if text.startswith("rtmp://"):
            user_data[chat_id]['rtmp'] = text
            bot.send_message(chat_id, "زوين! دابا صيفط لي رابط M3U8:")
        else:
            bot.send_message(chat_id, "المرجو إدخال رابط RTMP صحيح (كيبدى بـ rtmp://).")
    elif 'm3u8' not in user_data[chat_id]:
        if text.startswith("http") and text.endswith(".m3u8"):
            user_data[chat_id]['m3u8'] = text
            bot.send_message(chat_id, "بداية البث...")
            start_stream(chat_id)
        else:
            bot.send_message(chat_id, "المرجو إدخال رابط M3U8 صحيح (كيبدى بـ http وكيخلص بـ .m3u8).")
    else:
        bot.send_message(chat_id, "البث ديالك شغال دابا.")

def start_stream(chat_id):
    global ffmpeg_process
    m3u8 = user_data[chat_id]['m3u8']
    rtmp = user_data[chat_id]['rtmp']

    with lock:
        if ffmpeg_process:
            bot.send_message(chat_id, "كاين بث شغال دابا، وقف الأول قبل ما تبدا جديد.")
            return

        command = [
            'ffmpeg',
            '-i', m3u8,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-f', 'flv',
            rtmp
        ]

        try:
            ffmpeg_process = subprocess.Popen(command)
            bot.send_message(chat_id, "البث بدا بنجاح!")
        except Exception as e:
            bot.send_message(chat_id, f"وقع خطأ: {str(e)}")
            ffmpeg_process = None

bot.polling()
