import logging
import telebot
from telebot import types
import coin_module
import tools_module
import users_module
import bot_controls
import shelve
import time
import sys
import os
import json
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s_%(levelname)s: %(message)s')

bot = telebot.TeleBot(tools_module.get_token()["something_unimportant"])





@bot.message_handler(commands=['start', 'refresh'])
def send_welcome(message):
    logging.debug(f'{__name__}.send_welcome() {message.from_user.username}(user_id:{message.from_user.id}):{message.text}')
    msg = bot.send_message(message.chat.id, 'Привет! Я отслеживаю котировки монет.')
    bot.register_next_step_handler(msg, auth(message))

def auth(message):
    time.sleep(2)
    if str(message.from_user.id) in users_module.get_users_id_list():
        logging.debug(f'{__name__}.auth() is user exist:{str(message.from_user.id) in users_module.get_users_id_list()}')
        msg = bot.reply_to(message, f'Добро пожаловать {message.from_user.username}')

        users=users_module.load_users_from_db()
        for user in users:    #Если пользователь имеется в базе данных то передать его объект с настройками дальше по коду
            if message.from_user.id==user.user_id:

                bot.register_next_step_handler(msg, check_quotes(message))
                break

    else:    #Если пользователя нет в БД то ничего не делать
        logging.debug(f'{__name__}.auth() {message.from_user.username} is user exist={str(message.from_user.id) in users_module.get_users_id_list()}')
        bot.reply_to(message, f'{message.from_user.username}, отказано в доступе')





@bot.message_handler(content_types=['text'])
def check_quotes(message):
    user_object=users_module.get_user_object(message.from_user.id)
    logging.debug(f'{__name__}.check_quotes() загружен пользователь {user_object.__dict__}')
    logging.debug(f'{__name__}.check_quotes() {message.from_user.username}(user_id:{message.from_user.id}), is private user: {str(message.from_user.id)==user_object.user_id}')

    if message.text == '/run' and str(message.from_user.id)==str(user_object.user_id):
        user_object.set_is_check_coin_running(True)
        user_object.save_user_config()
        bot.send_message(message.chat.id, 'Бот начал отслеживать котировки')
        coin_module.update_coin_list(message, bot, user_object)
    
    elif message.text == '/stop'and str(message.from_user.id)==str(user_object.user_id):
        user_object.set_is_check_coin_running(False)
        user_object.save_user_config()
        bot.send_message(message.chat.id, 'Бот перестал отслеживать котировки')
        coin_module.running_state(is_running=False)    #Возможно не нужно
    
    elif message.text == "/settings" and str(message.from_user.id)==str(user_object.user_id):    #Блок управления настройками пользователя с помощью клавиатуры
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text=f'Интервал (сек.) = {user_object.time_frame}', callback_data="time_frame"))
        markup.add(types.InlineKeyboardButton(
            text=f'Пороговое значение (%) = {user_object.alert_threshold}', callback_data="alert_threshold"))
        bot.send_message(
            message.chat.id, text="Какие настройки изменить?", reply_markup=markup)

    elif str(message.from_user.id) not in str(users_module.get_users_id_list()):
        bot.send_message(
            message.chat.id, text="Доступ запрещен.")

@bot.message_handler(content_types=['text'])
def set_time_frame(message):
    
    user_object=users_module.get_user_object(message.from_user.id)
    value = message.text.lower()

    if tools_module.get_number(value) == False:    # Проверка ввода числа
        bot.send_message(message.chat.id, 'Ошибка примения настроек!')

    else:
        logging.debug(f'{__name__}.set_time_frame() получено новое значение time_frame: {value}')
        user_object.set_time_frame(value)
        user_object.save_user_config()
        bot.send_message(message.chat.id, f'Настройки сохранены!')


@bot.message_handler(content_types=['text'])
def set_threshold(message):
    user_object=users_module.get_user_object(message.from_user.id)
    some_Value = message.text.lower()
 
    if tools_module.get_float_number(some_Value) == False:    # Проверка ввода вещественного числа
        bot.send_message(message.chat.id, 'Ошибка примения настроек!')

    else:
        user_object.set_alert_threshold(some_Value)
        user_object.save_user_config()
        bot.send_message(message.chat.id, f'Настройки сохранены!')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    answer = ''
    if call.data == 'time_frame':
        answer = bot.send_message(
            call.message.chat.id, 'Укажите время в секундах...')
        bot.register_next_step_handler(answer, set_time_frame)
    elif call.data == 'alert_threshold':
        answer = bot.send_message(
            call.message.chat.id, 'Укажите порог в процентах...')
        bot.register_next_step_handler(answer, set_threshold)

    # Удалить клавиатуру из чата
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id)


# ------исполняемый код скрипта-------

if __name__ == '__main__':

    while True:
        try:
            bot.polling(none_stop=True)
            user_input = input()
        except KeyboardInterrupt as e:    #Без этой строчки код будет выполняться бесконечно при любом количестве ошибок
            logging.debug(f'Завершение работы c помощью KeyboardInterrupt')
            sys.exit(0)
        except Exception as e:
            time.sleep(3)
            logging.debug(f'ERROR: {e}')
