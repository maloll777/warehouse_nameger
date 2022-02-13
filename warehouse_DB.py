import sqlite3

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

import warehouse_DB_conf
from orm_warehouse import *


class Warehouse:
    def __init__(self):
        # подключения к БД
        # так же на основе файла warehouse_DB_conf.TYPE_DB происходит выбор СУБД

        if warehouse_DB_conf.TYPE_DB.lower() == "SQLite3".lower():
            self._connect = sqlite3.connect(warehouse_DB_conf.PATH)
            self._cursor = self._connect.cursor()

    def _close_db(self):
        # отключение от БД
        self._connect.close()

    def find_code_product(self, id_product):
        # по артикулу товара информацию о нем
        # возвращает словарь со значениями либо None

        try :
            data = Product.get(Product.code_product==id_product)
        except :
            data = None
        if data is not None:
            data = {'code_product':data.code_product, 'product_name':data.product_name, 'ean_code':data.ean_code,
                'price':data.price, 'brand_name':data.brand_product, 'group':data.group_product,
               'subgroup':data.subgroup_product}
        return data

    def find_id_product_for_code_product(self, code_product):
        # ищет id товара из таблицы product по артиклу
        self._cursor.execute(f"""SELECT id FROM product 
                        WHERE
                        code_product = '{code_product}'; """)
        return self._cursor.fetchall()[0][0]

    def get_art_warehouse(self, warehouse_name):
        # по имени склада возращает его ID из списка складов
        self._cursor.execute(f"""SELECT id FROM Warehouse_list
            WHERE warehouse_name = ('{warehouse_name.upper()}')""")
        out = self._cursor.fetchone()

        if out is None:
            return -1
        return out[0]

    def get_art_product(self, code_product, warehouse_id):
        # возвращает артикул товара по id из таблицы product
        self._cursor.execute(
            f"""SELECT product.code_product FROM product JOIN warehouse ON product.id = warehouse.product 
                        WHERE 
                        warehouse.product = {code_product} AND warehouse.warehouse_name = {warehouse_id};;""")
        return self._cursor.fetchall()[0][0]

    def get_balance_product(self, warehouse_name='%', product='%'):
        # возвращает остаток по складам
        self._cursor.execute(
            f"""SELECT p.code_product, p.product_name, w.balance, wl.warehouse_name 
            FROM warehouse w 
            JOIN
            Warehouse_list wl ON w.warehouse_name = wl.id
            JOIN
            Product p ON w.product = p.id
            WHERE wl.warehouse_name LIKE '{warehouse_name}' AND p.code_product LIKE '{product}';"""
        )
        out = self._cursor.fetchone()
        if out is None:
            return out
        else:
            return out[2]

    def get_product_id_from_warehouse(self, product_id):
        # возвращает id продукта из таблицы warehouse по id товара из таблицы product
        self._cursor.execute(f"""SELECT id FROM warehouse 
                        WHERE
                        product = {product_id}""")
        return self._cursor.fetchall()[0][0]

    def create_operation_warehouse(self, doc_number, doc_status, doc_type, comment=""):
        # создает документ для перемещения между складами
        self._cursor.execute(f"""INSERT INTO operation_warehouse(doc_number, doc_status, doc_type, comment) 
                        VALUES
                        ('{doc_number}', '{doc_status}', {doc_type}, '{comment}'); """)
        self._connect.commit()

    def move_product_warehouse(self, product, warehouse_out, warehouse_in, count, doc_operation):
        # создает перемещение между складами
        product = self.find_id_product_for_code_product(product)
        self._cursor.execute("BEGIN TRANSACTION;")

        self._cursor.execute(
            f"""INSERT INTO product_move(product, warehouse_out, warehouse_in, count, doc_operation) 
            VALUES
            ({product}, {warehouse_out}, {warehouse_in}, {count}, {doc_operation}); """
        )

        self._cursor.execute(
            f"""UPDATE warehouse SET balance = balance - {count} 
                WHERE warehouse_name = {warehouse_out} AND product = {product}; """
        )

        self._cursor.execute(
            f"""INSERT INTO reserve(id_product_warehouse, balance, doc_number, active)
            VALUES
            ({product}, {count}, {doc_operation}, true); """
        )

        self._cursor.execute("COMMIT;")

        self._connect.commit()

    def delivery_product_warehouse(self, warehouse_name, product, add_count, address=''):
        # пополнение товара на складе

        add_count = int(add_count)
        current_balance = self.get_balance_product(warehouse_name, product)
        product = self.find_id_product_for_code_product(product)
        warehouse_name = self.get_art_warehouse(warehouse_name)
        if current_balance is None:
            self._cursor.execute(
                f"""INSERT INTO warehouse (warehouse_name, product, balance, address )
                            VALUES
                            ({warehouse_name},{product},{add_count},'{address}');"""
            )
            self._connect.commit()
        else:
            add_count += current_balance
            self._cursor.execute(
                f"""UPDATE warehouse 
                            SET balance = {add_count} 
                            WHERE warehouse_name = {warehouse_name} and product = {product};"""
            )
            self._connect.commit()

    def get_shipment_product(self, product, warehouse_out, count, doc_operation):
        # отгрузка товара клиенту со склада
        pass

    def cancel_shipment(self):
        # возврат товара от клиента
        pass


class WarehouseConsole(Warehouse):
    # работа в консоли

    def warehouse_loop(self):
        # консольный интерфейс менеджера БД

        command_dict = {'help': '', 'exit': '',
                        'find': self.find_code_product, 'balance': self.get_balance_product,
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
