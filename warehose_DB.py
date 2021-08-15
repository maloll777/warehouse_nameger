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
def get_product_id_from_warehouse(connect, product_id):
    # возвращает id продукта из таблицы warehouse по id товара из таблицы product
    cursor = connect.cursor()
    cursor.execute(f"""SELECT id FROM warehouse WHERE  product = {product_id}""")
    return cursor.fetchall()[0][0]


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
