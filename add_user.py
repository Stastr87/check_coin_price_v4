import shelve
import users_module
from pprint import pprint 

user=users_module.User_obj(user_id='1260842812',user_name='stnsvtrfnv')
pprint(f'{user.user_id} {user.user_name}')
user.add_user_to_db()

