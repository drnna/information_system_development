from database.DBcm import DBContextManager
from flask import current_app #глобальная переменная с глобальным конфигурационным словарю


def select_list(_sql: str, user_list):
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан') #как бы создаем ошибку
        else:
            cursor.execute(_sql, user_list)
            result = cursor.fetchall()
            schema = []
            for item in cursor.description:
                schema.append(item[0])
            print(schema)
    return result, schema


def select_dict(_sql, user_input: dict):
    #Преобразование словаря параметров в список
    user_list = []

    for key in user_input:
        user_list.append(user_input[key])
        print('user_list= in dict', user_list)

    result, schema = select_list(_sql, user_list)

    # Преобразование в список словарей
    result_dict=[]

    for item in result:
        result_dict.append(dict(zip(schema, item)))

    print(result_dict)
    return result_dict

