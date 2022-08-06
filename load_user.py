import logging
import users_module
import shelve
import os
from pprint import pprint
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s-%(levelname)s - %(message)s')


with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
    users_list=shelFile['users']
    print(f'Число пользователей:{len(users_list)}')
    for user in users_list:
        pprint(user.__dict__) #__dict__ - служебный атрибут, возвращает все артибуты объкта
         #pprint(user)


    pprint(list(shelFile.keys()))    #Показать все ключи в БД
    
