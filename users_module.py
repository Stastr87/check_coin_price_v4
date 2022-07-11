import logging
import shelve
import json
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s_%(levelname)s: %(message)s')

class User_obj(object):
    def __init__(self, user_name=None, user_id=None):
        self.user_name = user_name
        self.user_id = user_id

    def __repr__(self):
        user={}
        user.update({'user_name':self.user_name})
        user.update({'user_id':self.user_id})
        return json.dumps(user)

    def add_user_to_db(self):
        with shelve.open('db',flag="c") as shelFile:
            user_list=shelFile['users']
            user_list.append(self)
            shelFile['users']=user_list


def load_users_from_db():
    with shelve.open('db',flag="r") as shelFile:
        user_list=shelFile['users']
    return user_list

def get_users_id_list():
    users_id_list=[]
    user_list=load_users_from_db()
    for user in user_list:
        users_id_list.append(user.user_id)
    return users_id_list
