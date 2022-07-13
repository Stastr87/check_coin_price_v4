import shelve
import users_module
import os
users=[]
users.append(users_module.User_obj())

with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
    shelFile['users']=users