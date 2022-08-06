import coin_module_v2
import users_module
import shelve
from pprint import pprint


new_user_object=users_module.get_user_object("1260842812")

response_data, response_code = coin_module_v2.check_quotes()

with shelve.open('coin_db') as shelve_file:
    klist = list(shelve_file.keys())

actual_quotes = coin_module_v2.coin_filter(response_data, response_code, new_user_object)

for coin_name in klist:
    for item in actual_quotes:
        if coin_name==item["symbol"]:
            coin=coin_module_v2.load_coin_obj(coin_name)
            coin.update_price_matrix(item['price'], item['time'])
            coin_module_v2.save_coin_obj(coin)

