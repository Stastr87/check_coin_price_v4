import json
import logging
import os
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s_%(levelname)s: %(message)s')


def get_config():
    with open(os.path.abspath('config.json'), 'r') as config_file:
        config = json.loads(config_file.read())
    return config


def change_config(setting_name, some_value):
    config = get_config()
    if setting_name in config.keys():
        config.update({setting_name: some_value})
    with open(os.path.abspath('temp_config.json'), 'w') as config_file:
        config_file.write(json.dumps(config))
    os.remove(os.path.abspath('config.json'))
    os.rename(os.path.abspath('temp_config.json'), os.path.abspath('config.json'))


def get_token():
    with open(os.path.abspath('token.json'), 'r') as config_file:
        config = json.loads(config_file.read())
        config_file.close()
        return config


def save_data(json_data, file_name):  # Сохранение данных json в файл
    if not os.path.exists(os.path.abspath('temp')):
        os.makedirs(os.path.abspath('temp'))
    with open(os.path.abspath(os.path.join('.', 'temp', file_name)), 'w') as response_data_file:
        response_data_file.write(json.dumps(
            json_data, indent=4, sort_keys=True))
        response_data_file.close()


def get_number(someValue):
    try:    # Проверка что someValue преобразуется в число без ошибки
        someValue = int(someValue)
        is_true = True
    # Проверка на ошибку неверного формата (введены буквы)
    except ValueError:
        is_true = False
    return is_true


def get_float_number(someValue):
    try:    # Проверка что someValue преобразуется в число без ошибки
        someValue = float(someValue)
        is_true = True
    # Проверка на ошибку неверного формата (введены буквы)
    except ValueError:
        is_true = False
    return is_true
