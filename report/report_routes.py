from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
from report.report_model import (
    create_report,
    get_report_detail,
    get_report_config,
    get_available_reports,
    get_report_column_names,
    calculate_summary
)
from decorators.access import group_required

report_bp = Blueprint('report_bp', __name__, template_folder='templates')


@report_bp.route('/reports', methods=['GET'])
@group_required
def report_menu():
    return render_template('report_menu.html')


@report_bp.route('/reports/create', methods=['GET', 'POST'])
@group_required
def create_report_handler():
    if request.method == 'GET':
        return render_template('create_report.html',
                               available_reports=get_available_reports())

    # POST обработка
    try:
        report_type = request.form.get('report_type')
        year = int(request.form.get('year'))
        month = int(request.form.get('month'))
    except (ValueError, TypeError):
        return render_template('report_error.html',
                               message='Некорректные данные. Год и месяц должны быть числами.',
                               return_url=url_for('report_bp.create_report_handler'))

    # Валидация даты
    if year < 2000 or year > 2030 or month < 1 or month > 12:
        return render_template('report_error.html',
                               message='Некорректная дата. Год должен быть между 2000-2030, месяц 1-12.',
                               return_url=url_for('report_bp.create_report_handler'))

    # Проверка существования типа отчета
    available_reports_keys = [report['key'] for report in get_available_reports()]
    if report_type not in available_reports_keys:
        return render_template('report_error.html',
                               message=f'Неизвестный тип отчета: {report_type}',
                               return_url=url_for('report_bp.create_report_handler'))

    result = create_report(report_type, year, month)

    if result.status:
        flash(result.message, 'success')
        return redirect(url_for('report_bp.report_menu'))
    else:
        return render_template('report_error.html',
                               message=result.message,
                               return_url=url_for('report_bp.create_report_handler'))


@report_bp.route('/reports/view', methods=['GET', 'POST'])
@group_required
def view_reports():
    # Обработка GET запроса с параметрами (для ссылок из других мест)
    if request.method == 'GET' and request.args.get('report_type'):
        try:
            report_type = request.args.get('report_type')
            year = int(request.args.get('year'))
            month = int(request.args.get('month'))

            return process_report_view(report_type, year, month)

        except (ValueError, TypeError):
            flash('Некорректные параметры запроса.', 'error')

    # Обработка POST запроса (из формы)
    if request.method == 'POST':
        try:
            report_type = request.form.get('report_type')
            year = int(request.form.get('year'))
            month = int(request.form.get('month'))

            return process_report_view(report_type, year, month)

        except (ValueError, TypeError):
            flash('Некорректные данные. Год и месяц должны быть числами.', 'error')

    # GET запрос без параметров - показать форму
    return render_template('view_reports.html',
                           available_reports=get_available_reports())


def process_report_view(report_type: str, year: int, month: int):
    """Обработка просмотра отчета"""
    # Валидация даты
    if year < 2000 or year > 2030 or month < 1 or month > 12:
        flash('Некорректная дата. Год должен быть между 2000-2030, месяц 1-12.', 'error')
        return redirect(url_for('report_bp.view_reports'))

    # Проверка существования типа отчета
    available_reports_keys = [report['key'] for report in get_available_reports()]
    if report_type not in available_reports_keys:
        flash(f'Неизвестный тип отчета: {report_type}', 'error')
        return redirect(url_for('report_bp.view_reports'))

    # Получение данных отчета
    result = get_report_detail(report_type, year, month)
    config = get_report_config(report_type)

    if not config:
        flash(f'Конфигурация для отчета {report_type} не найдена', 'error')
        return redirect(url_for('report_bp.view_reports'))

    if result.status:
        # Вычисление сводных данных
        summary_data = calculate_summary(report_type, result.data)
        column_names = get_report_column_names(report_type)

        # Используем универсальный шаблон report_detail.html
        return render_template('report_detail.html',
                               report_details=result.data,
                               report_title=config['name'],
                               column_names=column_names,
                               month=month,
                               year=year,
                               message=result.message,
                               summary_data=summary_data,
                               show_summary=config.get('summary', {}).get('enabled', False))
    else:
        flash(result.message, 'error')
        return redirect(url_for('report_bp.view_reports'))