import telebot
from telebot import types

def add_keyboard(m, bot):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1=types.KeyboardButton("/settings")
    btn2=types.KeyboardButton("/run")
    btn3=types.KeyboardButton("/stop")
    # Добавляем кнопки в клавиатуру
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    bot.send_message(m.chat.id,'/settings-изменить параметры наблюдателя\n/run-запустить наблюдателя\n/stop-остановить наблюдателя', reply_markup=markup)