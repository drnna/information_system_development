from dataclasses import dataclass
from flask import current_app, session
from database.DBcm import DBContextManager
from database.sql_provider import SQLProvider
from database.select2 import select_dict
from datetime import datetime
import os


@dataclass
class OrderResult:
    status: bool
    message: str
    order_id: int = None


provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))


def get_available_dates():
    """Получить даты с доступными сеансами"""
    _sql = provider.get('available_dates.sql')
    return select_dict(_sql, {}) or []


def get_sessions_by_date(selected_date):
    """Получить сеансы на выбранную дату"""
    _sql = provider.get('sessions_by_date.sql')
    return select_dict(_sql, {'selected_date': selected_date}) or []


def get_all_tickets_for_session(session_id):
    """Получить ВСЕ билеты для сеанса (и проданные, и свободные)"""
    _sql = provider.get('all_tickets.sql')
    return select_dict(_sql, {'session_id': session_id}) or []


def get_available_tickets(session_id):
    """Получить только доступные билеты для сеанса"""
    _sql = provider.get('available_tickets.sql')
    return select_dict(_sql, {'session_id': session_id}) or []


def add_ticket_to_basket(session_id, ticket_id):
    """Добавить билет в корзину"""
    # Получаем информацию о билете из ВСЕХ билетов сеанса
    all_tickets = get_all_tickets_for_session(session_id)
    ticket_data = next((t for t in all_tickets if t['ticket_id'] == ticket_id), None)

    if not ticket_data:
        return False, 'Билет не найден'

    if ticket_data['is_sold'] == 1:
        return False, 'Этот билет уже продан'

    basket = session.get('basket', {})
    basket_key = f"{session_id}_{ticket_id}"

    # Добавляем билет в корзину
    ticket_data['basket_key'] = basket_key
    basket[basket_key] = ticket_data
    session['basket'] = basket

    return True, f'Билет добавлен (Ряд {ticket_data["riad"]}, Место {ticket_data["seat"]})'


def clear_basket():
    """Очистить корзину"""
    session.pop('basket', None)
    return True, 'Корзина очищена'


def get_basket():
    """Получить корзину из сессии"""
    return session.get('basket', {})


def save_ticket_order(user_id):
    """Сохранить заказ билетов"""
    basket = session.get('basket', {})

    if not basket:
        return OrderResult(status=False, message='Корзина пуста')

    try:
        with DBContextManager(current_app.config['db_config']) as cursor:
            if cursor is None:
                return OrderResult(status=False, message='Ошибка подключения к базе данных')

            # Получаем SQL запросы
            insert_order_sql = provider.get('insert_order.sql')
            insert_order_list_sql = provider.get('insert_order_list.sql')
            update_ticket_sql = provider.get('update_ticket.sql')

            if not all([insert_order_sql, insert_order_list_sql, update_ticket_sql]):
                return OrderResult(status=False, message='Ошибка: SQL запросы не найдены')

            # Проверяем, не были ли билеты куплены пока они были в корзине
            for ticket_key, ticket in list(basket.items()):
                all_tickets = get_all_tickets_for_session(ticket['session_id'])
                current_ticket_state = next(
                    (t for t in all_tickets if t['ticket_id'] == ticket['ticket_id']),
                    None
                )

                if current_ticket_state and current_ticket_state['is_sold'] == 1:
                    # Удаляем проданный билет из корзины
                    basket.pop(ticket_key, None)

            # Обновляем корзину в сессии
            session['basket'] = basket

            if not basket:
                return OrderResult(status=False,
                                   message='Все билеты из вашей корзины были куплены другими пользователями')

            # Создаем заказ
            cursor.execute(insert_order_sql, (user_id,))
            order_id = cursor.lastrowid

            if order_id is None:
                return OrderResult(status=False, message='Не удалось создать заказ')

            # Группируем билеты по сеансам
            sessions_tickets = {}
            for ticket in basket.values():
                sessions_tickets.setdefault(ticket['session_id'], []).append(ticket)

            # Сохраняем все билеты
            for session_id, tickets in sessions_tickets.items():
                ticket_amount = len(tickets)
                total_price = sum(float(ticket['price']) for ticket in tickets)

                # Добавляем запись в order_list
                cursor.execute(insert_order_list_sql,
                               (order_id, session_id, ticket_amount, total_price))

                # Обновляем статус билетов
                for ticket in tickets:
                    cursor.execute(update_ticket_sql, (ticket['ticket_id'],))

            # Очищаем корзину
            session.pop('basket', None)

            return OrderResult(
                status=True,
                message=f'Заказ №{order_id} оформлен! Билетов: {len(basket)}',
                order_id=order_id
            )

    except Exception as e:
        return OrderResult(status=False, message=f'Ошибка при оформлении заказа: {str(e)}')