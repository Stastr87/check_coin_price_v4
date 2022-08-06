import coin_module_v2
import users_module
from pprint import pprint


new_user_object=users_module.get_user_object("1260842812")

response_data, response_code = coin_module_v2.check_quotes()


actual_quotes = coin_module_v2.coin_filter(response_data, response_code, new_user_object)



coin_obj_list=coin_module_v2.update_coin_list_v2(actual_quotes)

