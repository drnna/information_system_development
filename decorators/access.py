from functools import wraps
from flask import session, redirect, url_for, current_app, request, render_template


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_group' in session:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('auth_bp.auth_index'))

    return wrapper


def group_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_group' not in session:
            return redirect(url_for('auth_bp.auth_index'))

        access = current_app.config['db_access']
        user_role = session.get('user_group')
        endpoint = request.endpoint  # Полное имя endpoint'а, например 'report_bp.create_report_handler'

        # Определяем тип операции на основе имени endpoint'а
        if endpoint and 'report_bp' in endpoint:
            if 'create' in endpoint:
                # Проверка прав на создание отчетов
                can_access = (user_role in access and
                              ('report_bp' in access[user_role] or 'reports_create' in access[user_role]))
                if not can_access:
                    return render_template('withoutaccess.html',
                                           message='У вас нет прав на создание отчетов',
                                           return_url=url_for('main_menu'))

            elif 'view' in endpoint:
                # Проверка прав на просмотр отчетов
                can_access = (user_role in access and
                              ('report_bp' in access[user_role] or 'reports_view' in access[user_role]))
                if not can_access:
                    return render_template('withoutaccess.html',
                                           message='У вас нет прав на просмотр отчетов',
                                           return_url=url_for('main_menu'))

            else:
                # Общая проверка для других операций с отчетами
                can_access = (user_role in access and
                              ('report_bp' in access[user_role] or
                               'reports_create' in access[user_role] or
                               'reports_view' in access[user_role]))
                if not can_access:
                    return render_template('withoutaccess.html',
                                           message='У вас нет прав на работу с отчетами',
                                           return_url=url_for('main_menu'))

        else:
            # Проверка для других блюпринтов
            user_request = endpoint.split('.')[0] if endpoint else ''
            if user_role in access and user_request in access[user_role]:
                return func(*args, **kwargs)
            else:
                return render_template('withoutaccess.html',
                                       message='У вас нет прав на эту функциональность',
                                       return_url=url_for('main_menu'))

        return func(*args, **kwargs)

    return wrapper