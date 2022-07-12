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
    global private_user
    private_user=None
    user_id = message.from_user.id
    users_id_list=users_module.get_users_id_list()
    if str(user_id) in users_id_list:
        logging.debug(f'{__name__}.auth() is user exist={str(user_id) in users_id_list}')
        msg = bot.reply_to(message, f'Добро пожаловать {message.from_user.username}')
        bot.register_next_step_handler(msg, check_quotes)
        private_user=True
    else:
        logging.debug(f'{__name__}.auth() is user exist={str(user_id) in users_id_list}')
        bot.reply_to(message, f'{message.from_user.username}, отказано в доступе')
        private_user=False



@bot.message_handler(content_types=['text'])
def check_quotes(message):
    logging.debug(f'{__name__}.check_quotes() {message.from_user.username}(user_id:{message.from_user.id}), is private user={private_user}')
    if message.text == '/run' and private_user==True:
        with shelve.open('db',flag="c") as shelFile:
            is_check_coin_running=True
            shelFile['is_check_coin_running']=is_check_coin_running

        bot.send_message(message.chat.id, 'Бот начал отслеживать котировки')
        coin_module.update_coin_list(message, bot)
    
    elif message.text == '/stop' and private_user==True:
        with shelve.open('db',flag="c") as shelFile:
            is_check_coin_running=False
            shelFile['is_check_coin_running']=is_check_coin_running
        
        bot.send_message(message.chat.id, 'Бот перестал отслеживать котировки')
        coin_module.running_state(is_running=False)
    
    elif message.text == "/settings" and private_user==True:  # изменение конфига
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text=f'Интервал (сек.) = {tools_module.get_config()["time_frame"]}', callback_data="time_frame"))
        markup.add(types.InlineKeyboardButton(
            text=f'Пороговое значение (%) = {tools_module.get_config()["alert_threshold"]}', callback_data="alert_threshold"))
        bot.send_message(
            message.chat.id, text="Какие настройки изменить?", reply_markup=markup)
    elif private_user==False:
        bot.send_message(
            message.chat.id, text="Доступ запрещен.")

@bot.message_handler(content_types=['text'])
def set_time_frame(message, setting_name):
    # Проверка ввода числа
    some_Value = message.text.lower()
    if tools_module.get_number(some_Value) == False:
        bot.send_message(message.chat.id, 'Ошибка примения настроек!')
    else:
        tools_module.change_config(setting_name, some_Value)
        bot.send_message(message.chat.id, f'Настройки сохранены!')


@bot.message_handler(content_types=['text'])
def set_threshold(message, setting_name):
    # Проверка ввода числа
    some_Value = message.text.lower()
    if tools_module.get_float_number(some_Value) == False:
        bot.send_message(message.chat.id, 'Ошибка примения настроек!')
    else:
        tools_module.change_config(setting_name, some_Value)
        bot.send_message(message.chat.id, f'Настройки сохранены!')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    answer = ''
    if call.data == 'time_frame':
        answer = bot.send_message(
            call.message.chat.id, 'Укажите время в секундах...')
        bot.register_next_step_handler(answer, set_time_frame, call.data)
    elif call.data == 'alert_threshold':
        answer = bot.send_message(
            call.message.chat.id, 'Укажите порог в процентах...')
        bot.register_next_step_handler(answer, set_threshold, call.data)

    # Удалить клавиатуру из чата
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id)


# ------исполняемый код скрипта-------

if __name__ == '__main__':

    while True:
        try:
            bot.polling(none_stop=True)
            user_input = input()
        except KeyboardInterrupt:    #Без этой строчки код будет выполняться бесконечно при любом количестве ошибок
            sys.exit(0)
        except Exception as e:
            time.sleep(3)
            logging.debug(f'ERROR: {e}')
