from pymysql import connect
from pymysql.err import OperationalError

class DBContextManager:
    def __init__(self, db_connect: dict):
        self.conn = None
        self.cursor = None
        self.db_connect = db_connect

    def __enter__(self):
        try:
            self.conn = connect(**self.db_connect) # Подключение к MySQL
            self.cursor = self.conn.cursor() # Создание курсора
            self.conn.begin() #start transaction
            return self.cursor  # Возвращает курсор для работы
        except OperationalError as err:
            print(err.args)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb): # тип, значение и место ошибки аргументы в ()
        if exc_type:
            print(exc_type)
            print(exc_val)
        if self.cursor:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        return True