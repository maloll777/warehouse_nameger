import sqlite3
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

import warehouse_DB_conf


class Warehouse:

    connect = None

    def warehouse_loop(self):
        # консольный интерфейс менеджера БД
        while True:
            command_dict = {'find': self.find_code_product, 'help': '', 'exit': ''}
            sql_completer = WordCompleter(command_dict.keys())
            command_run = prompt('manager### ', completer=sql_completer).lower()
            command, *parametrs = command_run.strip().split()

            if command == 'help':
                print(*command_dict.keys())
                continue
            elif command == 'exit':
                break
            elif command not in command_dict.keys():
                print('команда не найдена')
                continue
            elif len(parametrs) < 1:
                print('мало параметров')
                continue
            elif len(parametrs) > 1:
                print('результат поиска только по первому параметру')

            print(command_dict[command](*parametrs))

    def connect_db(self):
        # подключения к БД
        # так же на основе файла warehouse_DB_conf.TYPE_DB происходит выбор СУБД

        if warehouse_DB_conf.TYPE_DB == "SQLite3":
            self.connect = sqlite3.connect(warehouse_DB_conf.PATH)

    def close_db(self):
        # отключение от БД
        self.connect.close()

    def find_code_product(self, id_product):
        # по артикулу товара информацию о нем
        cursor = self.connect.cursor()
        cursor.execute(f"""SELECT code_product, product_name, subgroup_product, group_product FROM product 
                        WHERE 
                        code_product LIKE '{id_product}';""")
        # return cursor.fetchone(self)[0]
        return cursor.fetchone()

    def get_art_product(self, code_product, warehouse_id):
        # возвращает артикул товара по id из таблицы product
        cursor = self.connect.cursor()
        cursor.execute(f"""SELECT product.code_product FROM product JOIN warehouse ON product.id = warehouse.product 
                        WHERE 
                        warehouse.product = {code_product} AND warehouse.warehouse_name = {warehouse_id};;""")
        return cursor.fetchall()[0][0]

    def add_product_warehouse(self, warehouse_name, product, address="", balance=1):
        # добавляет id товара которого небыло ранее на складе
        cursor = self.connect.cursor()
        cursor.execute(f"""INSERT INTO warehouse(warehouse_name, product, address, balance) 
                        VALUES
                        ({warehouse_name}, {product}, '{address}', {balance})""")
        self.connect.commit()

    def create_operation_warehouse(self, doc_number, doc_status, doc_type, comment=""):
        # создает документ для перемещения между складами
        cursor = self.connect.cursor()
        cursor.execute(f"""INSERT INTO operation_warehouse(doc_number, doc_status, doc_type, comment) 
                        VALUES
                        ('{doc_number}', '{doc_status}', {doc_type}, '{comment}'); """)
        self.connect.commit()

    def find_id_product_for_code_product(self, code_product):
        # ищет id товара из таблицы product по артиклу
        cursor = self.connect.cursor()
        cursor.execute(f"""SELECT id FROM product 
                        WHERE
                        code_product = '{code_product}'; """)
        return cursor.fetchall()[0][0]

    def get_product_id_from_warehouse(self, product_id):
        # возвращает id продукта из таблицы warehouse по id товара из таблицы product
        cursor = self.connect.cursor()
        cursor.execute(f"""SELECT id FROM warehouse 
                        WHERE
                        product = {product_id}""")
        return cursor.fetchall()[0][0]

    def move_product_warehouse(self, product, warehouse_out, warehouse_in, count, doc_operation):
        # создает перемещение между складами
        cursor = self.connect.cursor()
        product = self.find_id_product_for_code_product(product)
        cursor.execute("START TRANSACTION;")

        cursor.execute(
            f"""INSERT INTO product_move(product, warehouse_out, warehouse_in, count, doc_operation) 
            VALUES
            ({product}, {warehouse_out}, {warehouse_in}, {count}, {doc_operation}); """
        )

        cursor.execute(
            f"""UPDATE warehouse SET balance = balance - {count} 
                WHERE warehouse_name = {warehouse_out} AND product = {product}; """
        )

        cursor.execute(
            f"""INSERT INTO reserve(id_product_warehouse, balance, doc_number, active)
            VALUES
            ({self.get_product_id_from_warehouse(product)}, {count}, {doc_operation}, true); """
        )

        self.connect.commit()

    def get_shipment_product(self, product, warehouse_out, count, doc_operation):
        # отгрузка товара клиенту со склада
        cursor = self.connect.cursor()

        product_warehouse = self.find_id_product_for_code_product(product)
        product_reserve = self.get_product_id_from_warehouse(product_warehouse)

        cursor.execute(f"""START TRANSACTION;""")
        cursor.execute(f"""INSERT INTO 
                reserve(id_product_warehouse, balance, doc_number, active)
                VALUES
                ({product_reserve}, {count}, {doc_operation}, true)""")
        cursor.execute(f"""UPDATE warehouse
                SET
                balance = balance - {count}
                WHERE
                product = {product_warehouse} AND warehouse_name = {warehouse_out};""")

        self.connect.commit()

    def cancel_shipment(self):
        # возврат товара от клиента
        pass

    def get_balance_product(self):
        # возвращает остаток по складам
        pass

    def delivery_product_warehouse(self):
        # пополнение товара на складе
        pass
