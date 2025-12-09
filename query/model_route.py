from dataclasses import dataclass
from database.select import select_dict


@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str


def model_route(provider, user_input: dict, sql_file):
    """Выполняет SQL запрос и возвращает результат"""
    err_message = ''
    try:
        _sql = provider.get(sql_file)
        result = select_dict(_sql, user_input)

        if result:
            return ResultInfo(result=result, status=True, err_message=err_message)
        else:
            err_message = 'Данные не найдены'
            return ResultInfo(result=None, status=False, err_message=err_message)

    except Exception as e:
        err_message = f'Ошибка при выполнении запроса: {str(e)}'
        return ResultInfo(result=None, status=False, err_message=err_message)