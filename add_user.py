import shelve
import users_module
from pprint import pprint 


user=users_module.User_obj(user_id='438820340',user_name='jdoom64')
pprint(f'{user.user_id} {user.user_name}')
user.add_user_to_db()

