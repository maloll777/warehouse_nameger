import sqlite3

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from peewee import DoesNotExist

import warehouse_DB_conf
from orm_warehouse import *


class WarehouseClass:
    def __init__(self):
        # подключения к БД
        # так же на основе файла warehouse_DB_conf.TYPE_DB происходит выбор СУБД

        if warehouse_DB_conf.TYPE_DB.lower() == "SQLite3".lower():
            self._connect = sqlite3.connect(warehouse_DB_conf.PATH)
            self._cursor = self._connect.cursor()

    def _close_db(self):
        # отключение от БД
        self._connect.close()

    def get_info_product(self, id_product):
        # по артикулу товара информацию о нем
        # возвращает словарь со значениями либо None

        try:
            data = Product.get(Product.code_product == id_product)
        except DoesNotExist:
            data = None

        if data is not None:
            data = {'code_product': data.code_product, 'product_name': data.product_name, 'ean_code': data.ean_code,
                    'price': data.price, 'brand_name': data.brand_product, 'group': data.group_product,
                    'subgroup': data.subgroup_product}
        return data

    def get_id_product(self, find_code):
        # ищет id товара из таблицы product по артиклу
        try:
            data = Product.get(Product.code_product == find_code)
        except DoesNotExist:
            data = None
        return data

    def get_id_warehouse(self, warehouse_name):
        # по имени склада возращает его ID из списка складов

        try:
            data = Warehouse_list.get(Warehouse_list.warehouse_name == warehouse_name.upper())
        except DoesNotExist:
            data = None

        return data

    def get_balance_product(self, warehouse_name, product):
        # возвращает остаток по складам

        id_product = self.get_id_product(product)
        id_warehouse = self.get_id_warehouse(warehouse_name)

        try:
            data = Warehouse.get((Warehouse.warehouse_id == id_warehouse)
                                 & (Warehouse.product_id == id_product)).balance
        except DoesNotExist:
            data = None
        return data

    def create_operation_warehouse(self, doc_number, doc_status, doc_type, comment=""):
        # создает документ для перемещения между складами
        pass

    def add_product_reserve(self, product, warehouse_out, warehouse_in, count, doc_operation):
        # резервирует товар для перемещения
        pass

    def ship_product_reserve(self):
        # отгрузка накладной с товаром из резерва
        pass

    def delivery_product_warehouse(self, warehouse_name, product, add_count, address_product=''):
        # пополнение товара на складе

        add_count = int(add_count)
        current_balance = self.get_balance_product(warehouse_name, product)
        product = self.get_id_product(product)
        warehouse_name = self.get_id_warehouse(warehouse_name)
        if current_balance is None:
            Warehouse.create(product_id=product, warehouse_id=warehouse_name,
                             balance=add_count, address=address_product).save()
        else:
            add_count += current_balance
            raw = Warehouse.get(Warehouse.warehouse_id == warehouse_name and Warehouse.product_id == product)
            raw.balance = add_count
            raw.save()

    def cancel_shipment(self):
        # возврат товара от клиента
        pass


class WarehouseConsole(WarehouseClass):
    # работа в консоли

    def warehouse_loop(self):
        # консольный интерфейс менеджера БД

        command_dict = {'help': '', 'exit': '',
                        'find': self.get_info_product, 'balance': self.get_balance_product,
                        'delivery': self.delivery_product_warehouse
                        }
        sql_completer = WordCompleter(list(command_dict.keys()))

        run_loop = True
        while run_loop:

            command_run = prompt('manager### ',
                                 completer=sql_completer,
                                 history=FileHistory('warehouse_history.txt'),
                                 auto_suggest=AutoSuggestFromHistory()
                                 )
            command, *parameters = command_run.strip().split()

            if command == 'help':
                print(*command_dict.keys())
                continue
            elif command == 'exit':
                run_loop = False
                self._close_db()
            elif command not in command_dict.keys():
                print('команда не найдена')
                continue
            elif len(parameters) < 1:
                print('мало параметров')
                continue
            elif len(parameters) > 1 and command == 'find':
                print('результат поиска только по первому параметру')

            if run_loop:
                print(command_dict[command](*parameters))
