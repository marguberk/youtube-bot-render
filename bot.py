import os
import telebot
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import re
import locale

# Получаем токен из переменной окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на YouTube видео, и я верну тебе MP3 файл.")

@bot.message_handler(func=lambda message: True)
def handle_url(message):
    url = message.text.strip()
    
    # Проверяем, является ли сообщение ссылкой на YouTube
    if not is_youtube_url(url):
        bot.reply_to(message, "Пожалуйста, отправьте корректную ссылку на YouTube видео.")
        return
    
    try:
        # Отправляем сообщение о начале загрузки
        processing_msg = bot.reply_to(message, "⏳ Начинаю загрузку и конвертацию...")
        
        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    percent = d['_percent_str']
                    bot.edit_message_text(
                        f"⏳ Загрузка: {percent}",
                        message.chat.id,
                        processing_msg.message_id
                    )
                except:
                    pass

        # Настройки для загрузки
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'outtmpl': './tmp/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'max_filesize': 50000000
        }
        
        # Загружаем аудио
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            audio_file = f"{title}.mp3"
            
            # Очищаем название файла от специальных символов
            safe_title = re.sub(r'[^\w\-_\. ]', '_', title)
            safe_audio_file = f"{safe_title}.mp3"
            os.rename(audio_file, safe_audio_file)
            
            # Проверяем размер видео
            if info.get('filesize', 0) > 50000000:  # 50MB
                bot.edit_message_text(
                    "❌ Видео слишком большое. Пожалуйста, выберите видео короче.",
                    message.chat.id,
                    processing_msg.message_id
                )
                return
            
            # Отправляем аудио файл
            with open(safe_audio_file, 'rb') as audio:
                bot.edit_message_text(
                    "✅ Загрузка завершена! Отправляю файл...",
                    message.chat.id,
                    processing_msg.message_id
                )
                bot.send_audio(
                    message.chat.id,
                    audio,
                    title=title,
                    performer="YouTube Audio"
                )
            
            # Удаляем временный файл
            os.remove(safe_audio_file)
            bot.delete_message(message.chat.id, processing_msg.message_id)
        
    except Exception as e:
        error_message = str(e)
        if "Video unavailable" in error_message:
            bot.edit_message_text(
                "❌ Видео недоступно или является приватным",
                message.chat.id,
                processing_msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Произошла ошибка: {error_message}",
                message.chat.id,
                processing_msg.message_id
            )

def is_youtube_url(url):
    try:
        parsed = urlparse(url)
        return 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc
    except:
        return False

# Запускаем бота
bot.polling(none_stop=True) 