import telebot
import subprocess
import os
import signal

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
user_data = {}
processes = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "مرحبا! صيفط لي رابط RTMPS:")
    user_data[chat_id] = {}

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    chat_id = message.chat.id
    if chat_id in processes and processes[chat_id] is not None:
        processes[chat_id].terminate()
        bot.send_message(chat_id, "تم توقيف البث.")
        processes[chat_id] = None
    else:
        bot.send_message(chat_id, "ما كاين حتى بث شغال.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        bot.send_message(chat_id, "بدا بالأمر /start أولاً.")
        return

    if 'rtmps' not in user_data[chat_id]:
        if text.startswith("rtmps://"):
            user_data[chat_id]['rtmps'] = text
            bot.send_message(chat_id, "زوين! دابا صيفط لي رابط M3U8:")
        else:
            bot.send_message(chat_id, "المرجو إدخال رابط RTMPS صحيح.")
    elif 'm3u8' not in user_data[chat_id]:
        if text.startswith("http") and text.endswith(".m3u8"):
            user_data[chat_id]['m3u8'] = text
            bot.send_message(chat_id, "بداية البث...")
            start_stream(chat_id)
        else:
            bot.send_message(chat_id, "المرجو إدخال رابط M3U8 صحيح.")
    else:
        bot.send_message(chat_id, "البث بدا بالفعل.")

def start_stream(chat_id):
    m3u8 = user_data[chat_id]['m3u8']
    rtmps = user_data[chat_id]['rtmps']

    command = [
        'ffmpeg',
        '-re',
        '-i', m3u8,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-f', 'flv',
        rtmps
    ]

    try:
        process = subprocess.Popen(command)
        processes[chat_id] = process
        bot.send_message(chat_id, "البث بدا بنجاح.")
    except Exception as e:
        bot.send_message(chat_id, f"وقعت شي مشكل: {str(e)}")

bot.polling()