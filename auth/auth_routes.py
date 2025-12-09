from flask import render_template, request, session, redirect, url_for, flash, Blueprint
from auth.auth_model import authenticate_user
from decorators.access import login_required, group_required  # Добавляем импорт

auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')

@auth_bp.route('/auth', methods=['GET'])
def auth_index():
    return render_template('login.html')

@auth_bp.route('/auth', methods=['POST'])
def auth_login():
    login = request.form.get('login')
    password = request.form.get('password')

    auth_result = authenticate_user(login, password)

    if auth_result.status:
        session['user_id'] = auth_result.user_data['user_id']
        session['user_login'] = auth_result.user_data['login']
        session['user_group'] = auth_result.user_data['user_group']

        return redirect(url_for('main_menu'))
    else:
        flash(auth_result.err_message, 'error')
        return render_template('login.html')

@auth_bp.route('/logout')
def auth_logout():
    session.clear()
    return render_template('stop.html')