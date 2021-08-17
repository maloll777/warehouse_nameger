import psycopg2


def db_connect(func) -> object:
    # декоратор для подключения к БД
    connect = psycopg2.connect(
        database="triol",
        user="postgres",
        password="",
        host="127.0.0.1",
        port="5432"
    )

    def wrapper(*arg):
        return func(connect, *arg)

    return wrapper


@db_connect
def find_code_product(connect, id_product):
    # по id товара информацию о нем
    cursor = connect.cursor()
    cursor.execute("select code_product, product_name, subgroup_product, group_product from product where "
                   "code_product = '{}';".format(id_product))
    return cursor.fetchall()


@db_connect
def get_id_product(connect, code_product, warehouse_id):
    # возвращает артикул товара по id из таблицы product
    cursor = connect.cursor()
    cursor.execute("SELECT product.code_product FROM product JOIN warehouse ON product.id = warehouse.product WHERE "
                   "warehouse.product = {} AND warehouse.warehouse_name = {};;".format(code_product, warehouse_id))
    return cursor.fetchall()[0][0]


@db_connect
def reservation_product():
    # резервирование товара на складе
    pass


@db_connect
def add_product_warehouse(connect, warehouse_name, product, address="", balance=1):
    # добавляет id товара которого небыло ранее на складе
    cursor = connect.cursor()
    cursor.execute("""INSERT INTO warehouse(warehouse_name, product, address, balance) VALUES"
                   " ({}, {}, '{}', {})""".format(warehouse_name, product, address, balance))
    connect.commit()


@db_connect
def create_operation_warehouse(connect, doc_number, doc_status, doc_type, comment=""):
    # создает документ для перемещения между складами
    cursor = connect.cursor()
    cursor.execute(
        f"""INSERT INTO 
        operation_warehouse(doc_number, doc_status, doc_type, comment) 
        VALUES ('{doc_number}', '{doc_status}', {doc_type}, '{comment}'); """
                   )
    connect.commit()


@db_connect
def find_id_product_for_code_product(connect, code_product):
    # ищет id товара из таблицы product по артиклу
    cursor = connect.cursor()
    cursor.execute(f"""SELECT id FROM product WHERE code_product = '{code_product}'; """)
    return cursor.fetchall()[0][0]


@db_connect
def get_product_id_from_warehouse(connect, product_id):
    # возвращает id продукта из таблицы warehouse по id товара из таблицы product
    cursor = connect.cursor()
    cursor.execute(f"""SELECT id FROM warehouse WHERE  product = {product_id}""")
    return cursor.fetchall()[0][0]

@db_connect
def move_product_warehouse(connect, product, warehouse_out, warehouse_in, count, doc_operation):
    # создает перемещение между складами
    cursor = connect.cursor()
    product = find_id_product_for_code_product(product)
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
        ({get_product_id_from_warehouse(product)},
        {count}, {doc_operation}, true); """
    )

    #cursor.execute("COMMIT;")

    connect.commit()


@db_connect
def write_off_product():
    # списание товара со склада
    pass


@db_connect
def shipment_product():
    # отгрузка товара клиенту со склада
    pass


@db_connect
def cancel_shipment():
    # возврат товара от клиента
    pass


@db_connect
def get_balance_product():
    # возвращает остаток по складам
    pass
