import io
import os

import segno
import telebot
from telebot import types
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))
font = ImageFont.truetype(r'Montserrat-Regular.ttf', 96)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привіт')

@bot.message_handler(commands=['inform'])
def inform(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Надіслати квиток', callback_data='send_ticket')
    markup.add(btn1)
    bot.reply_to(message, 'За кнопкою нижче можна отримати квиток', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message_handler(message):
    if message.data == 'send_ticket':
        with open('ticket_bg.png', 'rb') as file:
            full_name = ' '.join([
                message.from_user.first_name or '',
                message.from_user.last_name or '',
            ])
            qr_code = segno.make_qr(';'.join([full_name]))
            out = io.BytesIO()
            qr_code.save(out, scale = 25, dark = 'darkblue', kind='png')
            out.seek(0)
            qr_img = Image.open(out)
            img = Image.open(file)
            img_width, img_height = img.size
            qr_width, qr_height = qr_img.size
            box = ((img_width - qr_width) // 2, (img_height - qr_height) // 2)
            img.paste(qr_img, box)
            draw = ImageDraw.Draw(img)
            draw.text((box[0], box[1] + qr_height + 20), full_name, font = font)

            bot.send_photo(message.from_user.id, img)
            # bot.send_message(message.from_user.id, full_name)
            # bot.send_photo(message.from_user.id, file)

bot.infinity_polling()