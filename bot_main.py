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

#@bot.message_handler(content_types=['text'])
def auth(message):
    time.sleep(2)

    if str(message.from_user.id) in users_module.get_users_id_list():
        logging.debug(f'{__name__}.auth() is user exist:{str(message.from_user.id) in users_module.get_users_id_list()}')

        keyboard_msg='/settings-изменить параметры наблюдателя\n/run-запустить наблюдателя\n/stop-остановить наблюдателя'
        bot_controls.add_keyboard(message.chat.id, bot, keyboard_msg)

        msg = bot.reply_to(message, f'Добро пожаловать {message.from_user.username}')


    else:    #Если пользователя нет в БД то ничего не делать
        logging.debug(f'{__name__}.auth() is user exist:{str(message.from_user.id) in users_module.get_users_id_list()}')
        msg = bot.reply_to(message, f'{message.from_user.username}, отказано в доступе')

    bot.register_next_step_handler(msg, main)


@bot.message_handler(commands=['run', 'stop','settings'])
def main(message):



    user_object=users_module.get_user_object(message.from_user.id)
    logging.debug(f'{__name__}.main() загружен пользователь {user_object.__dict__}')
    current_user_id=str(message.from_user.id)
    logging.debug(f'{__name__}.main() message from: {current_user_id}, {type(current_user_id)}')
    reply_msg=''
    if message.text == '/run' and current_user_id==user_object.user_id:
        user_object.set_is_check_coin_running(True)
        user_object.save_user_config()
        reply_msg='Запущено отслеживание котировок'
        bot_controls.add_keyboard(message.chat.id, bot, reply_msg)
        coin_module.update_coin_list(message, bot, user_object)


    elif message.text == '/stop'and current_user_id==user_object.user_id:
        user_object.set_is_check_coin_running(False)
        user_object.save_user_config()
        reply_msg='Бот перестал отслеживать котировки'
        bot_controls.add_keyboard(message.chat.id, bot, reply_msg)
    
    elif message.text == "/settings" and current_user_id==user_object.user_id:    #Блок управления настройками пользователя с помощью клавиатуры
        bot_controls.add_inline_keyboard(message,bot,user_object)
        
    elif current_user_id not in users_module.get_users_id_list():
        reply_msg='Доступ запрещен!'
        bot_controls.add_start_keyboard(message.chat.id, bot, reply_msg)


    logging.debug(f'{__name__}.main() {type(bot)}')
    logging.debug(f'{__name__}.main() MARK1')
    logging.debug(f'{__name__}.main() message.chat.id:{message.chat.id}')
    logging.debug(f'{__name__}.main() bot:{bot}')
 

    logging.debug(f'{__name__}.main() MARK2')

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
