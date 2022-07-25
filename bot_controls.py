import telebot
from telebot import types

def add_keyboard(chat_id, bot, keyboard_msg):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1=types.KeyboardButton("/settings")
    btn2=types.KeyboardButton("/run")
    btn3=types.KeyboardButton("/stop")
    # Добавляем кнопки в клавиатуру
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    bot.send_message(chat_id,keyboard_msg, reply_markup=markup)    #

def add_start_keyboard(chat_id, bot, keyboard_msg):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1=types.KeyboardButton("/start")
    # Добавляем кнопки в клавиатуру
    markup.add(btn1)
    bot.send_message(chat_id,keyboard_msg, reply_markup=markup)    


def add_inline_keyboard(message,bot,user_object):
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1=types.InlineKeyboardButton(text=f'Интервал (сек.) = {user_object.time_frame}', callback_data="time_frame")
        btn2=types.InlineKeyboardButton(text=f'Пороговое значение (%) = {user_object.alert_threshold}', callback_data="alert_threshold")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, text="Какие настройки изменить?", reply_markup=markup)