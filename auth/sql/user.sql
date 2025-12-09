SELECT u_id, login, user_group
        FROM internal_users
        WHERE login = %s AND password = %s