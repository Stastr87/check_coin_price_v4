import shelve
import users_module
import os
users=[]


with shelve.open(os.path.abspath('db'),flag="c") as shelFile:
    shelFile['users']=users