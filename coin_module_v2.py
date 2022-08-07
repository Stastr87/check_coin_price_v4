from ast import Break
import shelve
import requests
import os
import time
from datetime import datetime
import logging
import tools_module
import users_module
import pandas as pd

from pprint import pprint

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s-%(levelname)s - %(message)s')


class Coin_obj(object):
    def __init__(self, coin_name=None, price_matrix=None):
        self.coin_name=coin_name
        self.price_matrix=price_matrix
    
    def create_price_matrix(self):
        df=pd.DataFrame(columns=['timestamp','price'],index=[])
        self.price_matrix=df
        return self

    def update_price_matrix(self, price, time_stmp):
        dataFrame=self.price_matrix
        new_dataFrame=pd.DataFrame({'timestamp':time_stmp,
                                    'price':price},
                                    index=[0])
        frames=[dataFrame,new_dataFrame]
        updated_dataFrame=pd.concat(frames,ignore_index=True)
        self.price_matrix=updated_dataFrame
        return self

    def get_price_moving(self):
        #Тут должна быть формула, которая возвращает процент изменения максимальной и минимальной цены, последнюю актуальную цену
        pass

def save_coin_obj(coin_obj):
    with shelve.open('coin_db') as shelve_file:
        coin_name=coin_obj.coin_name
        shelve_file[coin_name]=coin_obj
        

def load_coin_obj(coin_name):
    with shelve.open('coin_db') as shelve_file:
        coin_obj=shelve_file[coin_name]
    return coin_obj



def check_quotes():  # Функция запроса котировок
    host = "https://fapi.binance.com"
    method = '/fapi/v1/ticker/price'
    headers = {'Content-type': 'application/json',
               'Content-Encoding': 'utf-8'}

    try:
        response = requests.get(f'{host}{method}', headers=headers)
        response_data, response_code = response.json(), response.status_code
        logging.debug(f'{__name__}.check_quotes() response.url={response.url} -> response_code: {response_code}')
    except:
        logging.debug(f'{__name__}.check_quotes() error to get response.url')
        response_data, response_code = 'Connection_error', None
    return response_data, response_code


def coin_filter(quotes, response_code, user_object):  # Фильтр тикеров согласно настройкам в конфиге
    new_quotes=[]
    if response_code == 200:
        for item in quotes:
            if item["symbol"][-1:] == user_object.coin_mask:
                new_quotes.append(item)
            # Сохраняются данные с примененым фильтром
    else:
        logging.debug(f'{__name__}.coin_filter(): FAIL to get response from server, response_code: {response_code}')
    return new_quotes

# Обновление котировок в БД объектов Coin_obj
def update_coin_list_v2(some_coin_list):  
    #Из общего списка сотировок выбираеются названия монет
    for item in some_coin_list:
        coin_name=item['symbol']
        #По названию монеты загружаются данные из БД
        coin_obj=load_coin_obj(coin_name)
        
        #Дополняются новыми данными
        coin_obj.update_price_matrix(item['price'], item['time'])
        #Обновленные данные сохраняются в БД
        save_coin_obj(coin_obj)


# Создает список из новых объектов Coin_obj
def create_new_coin_list(some_coin_list):
    
    new_coin_list = []
    for item in some_coin_list:
        coin=Coin_obj()
        coin.coin_name=item['symbol']
        coin.create_price_matrix()
        coin.update_price_matrix(item['price'], item['time'])
        new_coin_list.append(coin)
    return new_coin_list


# Возвращает цену и таймштамп переданного тикера
def check_price(quotes_json_data, coin):
    for item in quotes_json_data:
        if item['symbol'] == coin:
            price = item['price']
            time_stmp = item['time']

    return price, time_stmp


# Вносит изменения в список объектов Coin_obj
def get_alert_list(alert_threshold):
    alert_list=[]
    position=None
    with shelve.open('coin_db') as shelve_file:
        klist = list(shelve_file.keys())

    for coin_name in klist:
        coin=load_coin_obj(coin_name)
        df=coin.price_matrix

        #logging.debug(f'{__name__}.get_alert_list():{coin.coin_name} df.max()["price"]= {df.max()["price"]}')
        max=df.max()["price"]
        min=df.min()["price"]
        raw_open=df["price"].head(1)
        open=raw_open[0]
        raw_close=df["price"].tail(1)
        close=raw_close[len(df)-1]
        diff=float(max)-float(min)
        diff_percent=(diff/float(max))*100

        logging.debug(f'{__name__}.get_alert_list():{coin.coin_name} diff_percent= {diff_percent}, open= {open}, close= {close}')

        if diff_percent>=float(alert_threshold):

            #Если цена закрытия таймфрейма больше цены открытия, то LONG
            if open < close:
                position = "LONG"
            #Цена не изменилась считаем FLAT
            elif open==close:
                position = "FLAT"
            #Цена упала и считаем позицию SHORT
            else:
                position = "SHORT"
            #Создаем временный атрибуты объекта coin_obj 
            coin.price_moving=diff_percent
            coin.position=position
            #Сохраним данные в списке
            logging.debug(f'{__name__}.get_alert_list():  coin.position= {coin.position}')
            alert_list.append(coin)
    logging.debug(f'{__name__}.get_alert_list():  len(alert_list)= {len(alert_list)}')
    return alert_list

def clear_coin_db():
    with shelve.open('coin_db', flag="w") as shelve_file:
        shelve_file.clear()
        klist = list(shelve_file.keys())
    logging.debug(f'{__name__}.clear_coin_db():  klist= {klist}')

def delete_coin_db():
    file_name='coin_db'
    if os.path.isfile(file_name): 
        os.remove(file_name) 
        logging.debug(f'success removing file {file_name}') 
    else: 
        logging.debug("File doesn't exists!")


def retry(func):  # Декоратор функции в котором выполняется бесконечный цикл запросов
    def wrappedFunc(*args, **kwargs):
        is_check_coin_running=True
        while is_check_coin_running==True:
            logging.debug(f'{__name__}.is_check_coin_running: {is_check_coin_running}')
            logging.debug(f'{__name__}.wrappedFunc: {func.__name__}() called')
            _,is_check_coin_running=func(*args, **kwargs)
            logging.debug(f'{__name__}.wrappedFunc: {func.__name__}() return is_check_coin_running: {is_check_coin_running}')
            time.sleep(1)
    return wrappedFunc



@retry
def update_coin_list(message, bot, user_object):  # Обновление котировок в списке объектов Coin_obj
    #Очистить БД в начале процесса формирования сигналов
    delete_coin_db()

    #Получить актуальный конфиг пользователя
    user_id=user_object.user_id
    new_user_object=users_module.get_user_object(user_id)
    is_check_coin_running=new_user_object.is_check_coin_running
    alert_list=[]
    
    #Получаем новые котировки 
    response_data, response_code = check_quotes()
    #Фильтруем котировки 
    actual_quotes = coin_filter(response_data, response_code, new_user_object)
    new_coin_list=create_new_coin_list(actual_quotes)

    for coin in new_coin_list:
        save_coin_obj(coin)

    for i in range(int(new_user_object.time_frame)-1):
        if is_check_coin_running==False:
            pass

        else:
            #Получаем новые котировки 
            response_data, response_code = check_quotes()
            #Фильтруем котировки 
            actual_quotes = coin_filter(response_data, response_code, new_user_object)
            #Добавляем котировки в БД
            update_coin_list_v2(actual_quotes)
            #Накабливаем БД в течении количества секунд = time_frame
            time.sleep(1)

    #Получаем список монет "alert_list" согласно условию "alert_threshold"
    alert_list=get_alert_list(new_user_object.alert_threshold)

    #Отправляем сигналы в чат
    position = None
    for coin in alert_list:
        df=coin.price_matrix['price']
        #Последний элемент объекта DataFrame
        current_price = round(float(df.tail(1)), 5)
        price_moving = round(float(coin.price_moving), 2)
        position=coin.position
        if position=='SHORT':
            message_string = f"*{coin.coin_name}* (mov: -{price_moving}%),\n \U0001F4C9 *{position}*, close={current_price}"
        else:
            message_string = f"*{coin.coin_name}* (mov: {price_moving}%),\n \U0001F4C8 *{position}*, close={current_price}"
        bot.send_message(message.chat.id, message_string, parse_mode="Markdown")

    return alert_list, is_check_coin_running
