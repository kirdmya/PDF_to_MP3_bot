from gtts import gTTS
import pdfplumber
from pathlib import Path
import telebot
from time import sleep
import os

with open('token.txt', 'r') as file:
    token = file.readline().rstrip()

bot = telebot.TeleBot(token)

DIRECTORY_PATH = os.getcwd() + "\\"
photo = open(DIRECTORY_PATH + 'Фото\picture.png', 'rb')
@bot.message_handler(commands=['start'])
def start_handler(message):

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAMUYrTgFRRVd6t1x2ChENkaYaDKXwYAAi4AAyRxYhqI6DZDakBDFCkE')
    bot.send_chat_action(message.from_user.id, 'typing')
    sleep(1)

    bot.send_message(message.from_user.id, 'Привет, {} ✋'.format(message.from_user.first_name))
    bot.send_chat_action(message.from_user.id, 'typing')
    sleep(1)
    bot.send_message(message.from_user.id,
                     "Пришли мне текстовый файл в формате PDF 📝 \nЯ преобразую текст в речь и скину файл в формате MP3 🎧\nВ подписи укажи язык текста в формате 'en' или 'ru'❗")
    bot.send_chat_action(message.from_user.id, 'typing')
    sleep(1)
    bot.send_photo(message.from_user.id, photo)


@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        chat_id = message.chat.id

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_path = DIRECTORY_PATH + message.document.file_name

        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        if Path(file_path).is_file() and Path(file_path).suffix == '.pdf':
            print(f'[+] Original file: {Path(file_path).name}')
            print('[+] Processing...')
            with pdfplumber.PDF(open(file=file_path, mode='rb')) as pdf:
                pages = [page.extract_text() for page in pdf.pages]

            text = ''.join(pages)
            text = text.replace("\n", "")
            file_name = Path(file_path).stem  # получить название файла
            my_audio = gTTS(text=text, lang=message.caption, slow=False)

            bot.send_message(message.from_user.id, "Пожалуйста, подождите...")
            bot.send_chat_action(message.from_user.id, 'typing')


            my_audio.save(f'{file_name}.mp3')

            audio = open(DIRECTORY_PATH + f'{file_name}.mp3', 'rb')
            bot.send_audio(message.chat.id, audio)
            audio.close()



        else:
            bot.reply_to(message, 'Неверный формат, повторите попытку ⛔')
    except Exception as e:
        bot.reply_to(message, e)
    finally:
        if os.path.isfile(DIRECTORY_PATH + f'{file_name}.mp3'):
            os.remove(DIRECTORY_PATH + f'{file_name}.mp3')
            print("success")
        else:
            print("File doesn't exists!")

        if os.path.isfile(DIRECTORY_PATH + f'{file_name}.pdf'):
            os.remove(DIRECTORY_PATH + f'{file_name}.pdf')
            print("success")
        else:
            print("File doesn't exists!")
        print('[+] FINISH!')

bot.polling()
