import os


class SQLProvider:

    def __init__(self, file_path): # наследуемый метод -> ему управление передается сразу при обращении к классу
        self.scripts = {} # инициализация словаря
        for file in os.listdir(file_path):
            _sql = open(f'{file_path}/{file}').read() # заносим sql запрос в словарь, ключ - имя файла
            self.scripts[file] = _sql

    def get(self, file):
        _sql = self.scripts[file]
        return _sql
