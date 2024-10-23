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

user_states = {}
user_tickets = {}

# Привітання користувача
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привіт')

# Обробник команди inform
@bot.message_handler(commands=['inform'])
def inform(message):
    # Створюємо розмітку з кнопкою "Надіслати квиток"
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Надіслати квиток', callback_data='send_ticket')
    markup.add(btn1)
    bot.reply_to(message, 'За кнопкою нижче можна отримати квиток', reply_markup=markup)

# Обробник дії надіслати квиток
@bot.callback_query_handler(func=lambda callback: True)
def callback_message_handler(message):
    if message.data == 'send_ticket':
        # Беремо загальну фонову картинку
        with open('ticket_bg.png', 'rb') as file:
            full_name = ' '.join([
                message.from_user.first_name or '',
                message.from_user.last_name or '',
            ])
            # Створюємо QR код, далі накладаємо на фонове зображення
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

            # Надсилаємо зображення
            bot.send_photo(message.from_user.id, img)

            if message.from_user.id not in user_tickets:
                # Фіксуємо, що користувач отримав квиток
                user_tickets[message.from_user.id] = [full_name]

            # Надсилаємо нову клавіатуру з наступним підменю
            markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            btn1 = types.KeyboardButton('Купити ще')
            btn2 = types.KeyboardButton('Мої квитки')
            btn3 = types.KeyboardButton('Поділитись')
            markup.add(btn1, btn2, btn3)

            bot.send_message(message.from_user.id, 'Що хочете зробити далі?', reply_markup=markup)

# Обробник кнопки "Купити ще"
@bot.message_handler(func=lambda message: message.text == 'Купити ще')
def buy_more(message):
    # Показуємо наступне підменю
    user_states[message.chat.id] = 'buy_more'
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('Fan Zone')
    btn2 = types.KeyboardButton('VIP Zone 1')
    btn3 = types.KeyboardButton('VIP Zone 2')
    btn_back = types.KeyboardButton('Назад')

    markup.add(btn1, btn2, btn3)
    markup.add(btn_back)
    bot.send_message(message.chat.id, 'Оберіть, будь ласка, квитки:', reply_markup=markup)

# Обробник кнопки "Мої квитки"
@bot.message_handler(func=lambda message: message.text == 'Мої квитки')
def show_tickets(message):
    tickets = user_tickets.get(message.from_user.id, [])
    if tickets:
        ticket_list = '\n'.join(tickets)
        bot.send_message(message.chat.id, f'Ваші квитки:\n{ticket_list}')
    else:
        bot.send_message(message.chat.id, 'У вас ще немає квитків.')

# Обробник кнопки "Поділитись"
@bot.message_handler(func=lambda message: message.text == 'Поділитись')
def share_ticket(message):
    tickets = user_tickets.get(message.from_user.id, [])
    if tickets:
        ticket_info = '\n'.join(tickets)
        share_message = f'У мене є такі квитки:\n{ticket_info}\nПоділіться зі своїми друзями!'
        bot.send_message(message.chat.id, share_message)
    else:
        bot.send_message(message.chat.id, 'У вас немає квитків, щоб поділитися.')

# Обробник вибору квитка
@bot.message_handler(func=lambda message: message.text in ['Fan Zone', 'VIP Zone 1', 'VIP Zone 2'])
def select_zone(message):
    selected_zone = message.text
    user_states[message.chat.id] = 'zone_selected'

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('PrivatBank')
    btn2 = types.KeyboardButton('Monobank')
    btn3 = types.KeyboardButton('Ощадбанк')
    btn_back = types.KeyboardButton('Назад')
    btn_cancel = types.KeyboardButton('Скасувати')

    markup.add(btn1, btn2, btn3)
    markup.add(btn_back, btn_cancel)

    bot.send_message(message.chat.id, f'Ви обрали: {selected_zone}\nОберіть спосіб оплати:', reply_markup=markup)

# Обробник вибору банку для оплати
@bot.message_handler(func=lambda message: message.text in ['PrivatBank', 'Monobank', 'Ощадбанк'])
def payment_metod(message):
    selected_metod = message.text

    bot.send_message(message.chat.id, f'Ви обрали: {selected_metod}\nЩе не реалізовано')

# Обробник кнопки назад з купити ще
@bot.message_handler(func=lambda message: message.text == 'Назад' and user_states.get(message.chat.id) == 'buy_more')
def go_back_from_payment(message):
    user_states[message.chat.id] = 'main_menu'
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('Купити ще')
    btn2 = types.KeyboardButton('Мої квитки')
    btn3 = types.KeyboardButton('Поділитись')

    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'Що хочете зробити далі?', reply_markup=markup)

# Пропозиція купити ще
@bot.message_handler(func=lambda message: message.text == 'Назад' and user_states.get(message.chat.id) == 'zone_selected')
def go_back_from_selection(message):
    user_states[message.chat.id] = 'buy_more'
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('Fan Zone')
    btn2 = types.KeyboardButton('VIP Zone 1')
    btn3 = types.KeyboardButton('VIP Zone 2')
    btn_back = types.KeyboardButton('Назад')

    markup.add(btn1, btn2, btn3)
    markup.add(btn_back)

    bot.send_message(message.chat.id, 'Оберіть, будь ласка, квитки:', reply_markup=markup)

# Обробник кнопки "Скасувати"
@bot.message_handler(func=lambda message: message.text == 'Скасувати')
def cancel_operation(message):
    user_states[message.chat.id] = 'main_menu'

    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('Купити ще')
    btn2 = types.KeyboardButton('Мої квитки')
    btn3 = types.KeyboardButton('Поділитись')

    markup.add(btn1, btn2, btn3)

    bot.send_message(message.chat.id, 'Операцію скасовано. Що хочете зробити далі?', reply_markup=markup)


bot.infinity_polling()