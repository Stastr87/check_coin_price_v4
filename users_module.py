import logging
from pprint import pprint
import shelve
import json
import os

from matplotlib import rc_params_from_file
logging.basicConfig(level=logging.INFO,format='%(asctime)s_%(levelname)s: %(message)s')

class User_obj(object):
    def __init__(self, user_id, **settings):
        self.user_id = user_id
        for setting,value in settings.items():   #конструкция для обработки свободного набора настроек
            if setting=='user_name':
                self.user_name=value
            if setting=='coin_mask':
                self.coin_mask = value
            if setting=='time_frame':
                self.time_frame = value
            if setting=='alert_threshold':
                self.alert_threshold=value
            if setting=='is_check_coin_running':
                self.is_check_coin_running=value
    def get_user_id(self):
        return self.user_id
    def set_user_id(self, value):
        self.user_id=value

    def get_user_name(self):
        return self.user_name
    def set_user_name(self,value):
        self.user_name=value

    def get_coin_mask(self):
        return self.coin_mask
    def set_coin_mask(self,value):
        self.coin_mask=value

    def get_time_frame(self):
        return self.time_frame
    def set_time_frame(self,value):
        self.time_frame=value

    def get_alert_threshold(self):
        return self.alert_threshold
    def set_alert_threshold(self,value):
        self.alert_threshold=value

    def get_is_check_coin_running(self):
        return self.is_check_coin_running
    def set_is_check_coin_running(self,value):
        self.is_check_coin_running=value

    def __repr__(self):
        user={}
        user.update({'user_name':self.user_name})
        user.update({'user_id':self.user_id})
        return json.dumps(user)

    def add_user_to_db(self):
        if 'user_name' not in self.__dict__:
            self.user_name='New user'
        if 'coin_mask' not in self.__dict__:
            self.coin_mask='T'
        if 'time_frame' not in self.__dict__:
            self.time_frame=45
        if 'alert_threshold' not in self.__dict__:
            self.alert_threshold=1
        if 'is_check_coin_running' not in self.__dict__:
            self.is_check_coin_running=False

        with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
            user_list=shelFile['users']
            user_list.append(self)
            shelFile['users']=user_list


    def save_user_config(self):
        logging.debug(f'Получен объект для сохранения в БД: {self.__dict__}')
        with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
            temp_user_list=shelFile['users']
            for user in temp_user_list:
                if user.user_id==self.user_id:
                    logging.debug(f'self.__dict__: {self.__dict__}')
                    if 'user_name' in self.__dict__:
                        user.user_name=self.user_name
                    if 'coin_mask' in self.__dict__:
                        user.coin_mask=self.coin_mask
                    if 'time_frame' in self.__dict__:
                        user.time_frame=self.time_frame
                    if 'alert_threshold' in self.__dict__:
                        user.alert_threshold=self.alert_threshold
                    if 'is_check_coin_running' in self.__dict__:
                        user.is_check_coin_running=self.is_check_coin_running
                    break
            shelFile['users']=temp_user_list


def load_users_from_db():
    with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
        user_list=shelFile['users']
    return user_list

def get_user_object(user_id):
    logging.debug(f'{__name__}.get_user_object() Поиск пользователя {user_id} в БД')
    user_object=None
    users=load_users_from_db()
    for user in users:    #Если пользователь имеется в базе данных то передать его объект с настройками дальше по коду
        if str(user_id)==str(user.user_id):
            user_object=user
            break
    return user_object

def get_users_id_list():
    users_id_list=[]
    user_list=load_users_from_db()
    for user in user_list:
        users_id_list.append(user.user_id)
    return users_id_list

def get_user_config(user_id):
    user_list=load_users_from_db
    for user in user_list:
        if user.user_id==user_id:
            return user



