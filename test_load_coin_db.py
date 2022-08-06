import coin_module_v2
import shelve
from pprint import pprint

with shelve.open('coin_db', flag='r') as shelve_file:
    klist = list(shelve_file.keys())

pprint((coin_module_v2.load_coin_obj(klist[0])).__dict__)
for coin_name in klist:
    coin=coin_module_v2.load_coin_obj(coin_name)
    #pprint(coin.__dict__)