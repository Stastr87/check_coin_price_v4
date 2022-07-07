import logging
import telebot
from telebot import types
import coin_module
import tools_module
import bot_controls
import shelve
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s_%(levelname)s: %(message)s')

bot = telebot.TeleBot(tools_module.get_token()["something_unimportant"])

# Добавить команду /stop


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id,'Вас приветсвует бот для отслеживания котировок!')
    bot_controls.add_keyboard(m, bot)


@bot.message_handler(content_types=["text"])
def check_quotes(m):
    if m.text.strip() == '/run':
        with shelve.open('temp/tempData',flag="c") as shelFile:
            is_check_coin_running=True
            shelFile['is_check_coin_running']=is_check_coin_running

        bot.send_message(m.chat.id, 'Бот начал отслеживать котировки')
        coin_module.update_coin_list(m, bot)
    
    elif m.text.strip() =='/stop':
        with shelve.open('temp/tempData',flag="c") as shelFile:
            is_check_coin_running=False
            shelFile['is_check_coin_running']=is_check_coin_running
        
        bot.send_message(m.chat.id, 'Бот перестал отслеживать котировки')
        coin_module.running_state(is_running=False)
    
    elif m.text.strip() == "/settings":  # изменение конфига
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text=f'Интервал (сек.) = {tools_module.get_config()["time_frame"]}', callback_data="time_frame"))
        markup.add(types.InlineKeyboardButton(
            text=f'Пороговое значение (%) = {tools_module.get_config()["alert_threshold"]}', callback_data="alert_threshold"))
        bot.send_message(
            m.chat.id, text="Какие настройки изменить?", reply_markup=markup)
    

@bot.message_handler(content_types=['text'])
def set_time_frame(m, setting_name):
    # Проверка ввода числа
    some_Value = m.text.lower()
    if tools_module.get_number(some_Value) == False:
        bot.send_message(m.chat.id, 'Ошибка примения настроек!')
    else:
        tools_module.change_config(setting_name, some_Value)
        bot.send_message(m.chat.id, f'Настройки сохранены!')


@bot.message_handler(content_types=['text'])
def set_threshold(m, setting_name):
    # Проверка ввода числа
    some_Value = m.text.lower()
    if tools_module.get_float_number(some_Value) == False:
        bot.send_message(m.chat.id, 'Ошибка примения настроек!')
    else:
        tools_module.change_config(setting_name, some_Value)
        bot.send_message(m.chat.id, f'Настройки сохранены!')


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

bot.polling(none_stop=True, interval=0)
