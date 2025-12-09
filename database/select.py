from database.DBcm import DBContextManager
from flask import current_app  # Глобальная переменная с глобальным конфигурационным словарю


def select_list(_sql: str, param_list: list) -> tuple:
    with DBContextManager(current_app.config['db_config']) as cursor:
        result = None
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            cursor.execute(_sql, param_list) #выполнение параметризированного запроса
            result = cursor.fetchall() #
    return result

def select_dict(_sql, user_input:dict) -> tuple:
    user_list = []
    for key in user_input:
        user_list.append(user_input[key])
    print('user_list= in dict', user_list)
    result = select_list(_sql, user_list)
    return  result