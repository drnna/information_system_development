from flask import Blueprint, render_template, request, url_for, session
import os.path
import json
from database.sql_provider import SQLProvider
from query.model_route import model_route
from decorators.access import group_required

query_bp = Blueprint('query_bp', __name__, template_folder='templates')

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'query.json')
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    QUERIES_CONFIG = json.load(f)['queries']


@query_bp.route('/cinema')
@group_required
def cinema_handle():
    return render_template('request_menu.html',
                           available_queries=QUERIES_CONFIG)


@query_bp.route('/cinema/<query_type>', methods=['GET'])
@group_required
def query_input(query_type):
    if query_type not in QUERIES_CONFIG:
        return render_template('error.html',
                               error_message=f"Запрос '{query_type}' не найден",
                               back_url=url_for('query_bp.cinema_menu'))

    return render_template('input_information.html',
                           query_type=query_type,
                           query_config=QUERIES_CONFIG[query_type])


@query_bp.route('/cinema/<query_type>', methods=['POST'])
@group_required
def query_result(query_type):
    if query_type not in QUERIES_CONFIG:
        return render_template('error.html',
                               error_message=f"Запрос '{query_type}' не найден",
                               back_url=url_for('query_bp.cinema_menu'))

    query_config = QUERIES_CONFIG[query_type]
    user_input = request.form

    result_info = model_route(provider, user_input, sql_file=query_config['sql_file'])

    if result_info.status:
        return render_template('dynamic.html',
                               query_type=query_type,
                               query_config=query_config,
                               data=result_info.result)
    else:
        return render_template('error.html',
                               error_message=result_info.err_message,
                               back_url=url_for('query_bp.query_input', query_type=query_type))