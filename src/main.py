import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))

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
            bot.send_photo(message.from_user.id, file)
            first_name = message.from_user.first_name or ''
            last_name = message.from_user.last_name or ''
            bot.send_message(message.from_user.id, first_name + ' ' + last_name)

bot.infinity_polling()