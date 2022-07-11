import logging
import users_module
import shelve
from pprint import pprint
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s_%(levelname)s: %(message)s')

users_list=users_module.load_users_from_db()
pprint(users_list)

with shelve.open('db',flag="r") as shelFile:
    is_check_coin_running=shelFile['is_check_coin_running']
print(f'is_check_coin_running: {is_check_coin_running}')