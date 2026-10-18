import os
import logging
import telebot
from decouple import config
import requests

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

if not os.path.exists("downloads"):
    os.mkdir("downloads")

API_TOKEN = config("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

DOWNLOAD_DIR = "downloads/"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "Please enter the URL of the file that you want to download...")


def download_file(url):
    local_filename = url.split("/")[-1][:50]
    file_path = DOWNLOAD_DIR + local_filename
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return file_path


@bot.message_handler(func= lambda message: True)
def download_file_url(message):
    url = message.text
    try:
        file_path = download_file(url)
        bot.send_document(
            chat_id=message.chat.id,
            reply_to_message_id=message.id,
            document=open(file_path, "rb"),
            caption="File downloaded successfully, ENJOY!",
        )
        os.remove(file_path)
    except:
        bot.reply_to(message, "File download failed. Please check the URL and try again")


bot.infinity_polling()
