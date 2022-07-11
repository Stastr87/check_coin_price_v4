import shelve
import users_module

users=[]
users.append(users_module.User_obj())

with shelve.open('db',flag="c") as shelFile:
    shelFile['users']=users