from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from ticket.ticket_model import (
    get_available_dates, get_sessions_by_date, get_all_tickets_for_session,
    add_ticket_to_basket, clear_basket, get_basket, save_ticket_order
)
from decorators.access import group_required

ticket_bp = Blueprint('ticket_bp', __name__, template_folder='templates')


@ticket_bp.route('/tickets')
@group_required
def tickets_main():
    """Главная страница - выбор даты"""
    dates = get_available_dates()
    return render_template('ticket_dates.html', dates=dates)


@ticket_bp.route('/tickets/select', methods=['GET', 'POST'])
@group_required
def select_tickets():
    """Объединенная страница - сеансы + выбор мест + корзина"""
    selected_date = request.form.get('selected_date') or request.args.get('selected_date')
    session_id = request.form.get('session_id') or request.args.get('session_id')

    if not selected_date:
        flash('Дата не выбрана', 'ticket_error')
        return redirect(url_for('ticket_bp.tickets_main'))

    sessions = get_sessions_by_date(selected_date)
    # Теперь получаем ВСЕ билеты, включая проданные
    tickets = get_all_tickets_for_session(session_id) if session_id else []
    basket = get_basket()

    return render_template('ticket_selection.html',
                           sessions=sessions,
                           tickets=tickets,
                           basket=basket,
                           session_id=session_id,
                           selected_date=selected_date)


@ticket_bp.route('/tickets/add', methods=['POST'])
@group_required
def add_ticket():
    """Добавить билет в корзину"""
    session_id = request.form.get('session_id')
    ticket_id = request.form.get('ticket_id')
    selected_date = request.form.get('selected_date')

    if not all([session_id, ticket_id, selected_date]):
        flash('Билет не выбран', 'ticket_error')
    else:
        success, message = add_ticket_to_basket(session_id, int(ticket_id))
        flash(message, 'ticket_success' if success else 'ticket_error')

    return redirect(url_for('ticket_bp.select_tickets',
                            selected_date=selected_date,
                            session_id=session_id))


@ticket_bp.route('/tickets/clear', methods=['POST'])
@group_required
def clear_basket_route():
    """Очистить корзину"""
    selected_date = request.form.get('selected_date')
    session_id = request.form.get('session_id')

    clear_basket()
    flash('Корзина очищена', 'ticket_success')

    return redirect(url_for('ticket_bp.select_tickets',
                            selected_date=selected_date,
                            session_id=session_id))


@ticket_bp.route('/tickets/save', methods=['POST'])
@group_required
def save_order():
    """Сохранить заказ"""
    selected_date = request.form.get('selected_date')
    session_id = request.form.get('session_id')

    result = save_ticket_order(session.get('user_id'))

    if result is None:
        flash('Произошла непредвиденная ошибка при оформлении заказа', 'ticket_error')
    else:
        flash(result.message, 'ticket_success' if result.status else 'ticket_error')

    return redirect(url_for('ticket_bp.select_tickets',
                            selected_date=selected_date,
                            session_id=session_id))