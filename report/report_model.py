from dataclasses import dataclass
from database.select import select_dict
from database.DBcm import DBContextManager
from flask import current_app
import os
import json
from database.sql_provider import SQLProvider


@dataclass
class ReportResult:
    data: list
    status: bool
    message: str


provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'report.json')

with open(config_path, 'r', encoding='utf-8') as f:
    report_config = json.load(f)['reports']


def create_report(report_type: str, year: int, month: int):
    try:
        if report_type not in report_config:
            return ReportResult(None, False, f'Неизвестный тип отчета: {report_type}')

        report_config_data = report_config[report_type]
        report_name = report_config_data['name']
        procedure_name = report_config_data['procedure_name']

        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                return ReportResult(None, False, 'Ошибка подключения к БД')

            cursor.callproc(procedure_name, [month, year])
            result = cursor.fetchall()

            if not result or len(result) == 0:
                return ReportResult(None, False, 'Процедура не вернула результат')

            message = str(result[0][0])

            if 'already exists' in message.lower():
                return ReportResult(None, False, f' {report_name} за {month}/{year} уже существует')
            elif 'no data available' in message.lower():
                return ReportResult(None, False, f'Нет данных для создания отчета {report_name} за {month}/{year}')
            elif 'created successfully' in message.lower():
                return ReportResult(None, True, f' {report_name} за {month}/{year} успешно создан')
            else:
                return ReportResult(None, False, f'Неизвестный ответ от процедуры: {message}')

    except Exception as e:
        return ReportResult(None, False, f'Ошибка при создании отчета: {str(e)}')


def get_report_detail(report_type: str, year: int, month: int):
    try:
        if report_type not in report_config:
            return ReportResult(
                data=None,
                status=False,
                message=f'Неизвестный тип отчета: {report_type}'
            )

        report_config_data = report_config[report_type]
        table_name = report_config_data['table_name']
        report_name = report_config_data['name']

        base_sql = provider.get('get_report_detail.sql')
        _sql = base_sql.format(table_name=table_name)

        params_dict = {'month': month, 'year': year}
        result = select_dict(_sql, params_dict)

        if result:
            return ReportResult(
                data=result,
                status=True,
                message=f'Детали отчета {report_name} успешно загружены'
            )
        else:
            return ReportResult(
                data=[],
                status=True,
                message=f'Отчет {report_name} за {month}/{year} не найден'
            )

    except Exception as e:
        return ReportResult(
            data=None,
            status=False,
            message=f'Ошибка при загрузке деталей отчета: {str(e)}'
        )


def get_report_config(report_type: str = None):
    """Получить конфигурацию отчета по типу или все отчеты"""
    if report_type:
        return report_config.get(report_type, None)
    return report_config


def get_available_reports():
    """Получить список доступных отчетов"""
    reports_list = []
    for key, config in report_config.items():
        reports_list.append({
            'key': key,
            'name': config['name']
        })
    return reports_list


def get_report_column_names(report_type: str):
    """Получить названия колонок для отчета"""
    config = get_report_config(report_type)
    if config and 'column_names' in config:
        return config['column_names']
    return []


def calculate_summary(report_type: str, data: list):
    """Вычислить сводные данные для отчета"""
    if not data:
        return {}

    config = get_report_config(report_type)
    if not config or not config.get('summary', {}).get('enabled', False):
        return {}

    summary_config = config['summary']
    summary_data = {}

    if 'sum_columns' in summary_config and 'labels' in summary_config:
        # Получаем список колонок из конфигурации
        columns = config.get('columns', [])

        for column_name, column_label in summary_config['labels'].items():
            if column_name in columns:
                # Находим индекс колонки в списке колонок
                column_index = columns.index(column_name)

                # Проверяем, что data не пуста и имеет достаточную длину
                if data and len(data[0]) > column_index:
                    # Суммируем значения в этой колонке
                    total = 0
                    for row in data:
                        if len(row) > column_index:
                            try:
                                # Получаем значение из кортежа по индексу
                                value = row[column_index]
                                # Пробуем преобразовать в число
                                if value is not None:
                                    total += float(value)
                            except (ValueError, TypeError, IndexError) as e:
                                # Если не удалось преобразовать, продолжаем
                                continue

                    # Форматируем результат
                    if 'formatters' in summary_config and column_name in summary_config['formatters']:
                        total_str = f"{total}{summary_config['formatters'][column_name]}"
                    else:
                        total_str = str(total)

                    summary_data[column_label] = total_str

    return summary_data