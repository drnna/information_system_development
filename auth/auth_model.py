from dataclasses import dataclass
from flask import current_app
import os
from database.DBcm import DBContextManager
from database.sql_provider import SQLProvider


@dataclass
class AuthResult:
    user_data: dict
    status: bool
    err_message: str


# Инициализация провайдера SQL
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def authenticate_user(login: str, password: str):
    err_message = ''
    # Получаем SQL из файла
    _sql = provider.get('user.sql')

    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor:
            cursor.execute(_sql, (login, password))
            result = cursor.fetchone()
            if result:
                user_data = {
                    'user_id': result[0],
                    'login': result[1],
                    'user_group': result[2]
                }
                return AuthResult(user_data=user_data, status=True, err_message=err_message)

    err_message = 'Неверный логин или пароль'
    return AuthResult(user_data=None, status=False, err_message=err_message)