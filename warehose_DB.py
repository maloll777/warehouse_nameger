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
def find_code_product(cursor, id_product):
    # по id товара информацию о нем

    cursor.execute("select code_product, product_name, subgroup_product, group_product from product where "
                   "code_product = '{}';".format(id_product))
    return cursor.fetchall()

@db_connect
def get_id_product(connect, code_product, warehouse_id):
    # возвращает id товара из таблицы warehouse
    cursor = connect.cursor()
    cursor.execute("SELECT product.code_product FROM product JOIN warehouse ON product.id = warehouse.product WHERE "
                   "warehouse.product = {} AND warehouse.warehouse_name = {};;".format(code_product, warehouse_id ))
    return cursor.fetchall()[0][0]


@db_connect
def reservation_product(connect):
    # резервирование товара на складе
    pass


@db_connect
def add_product_warehouse(connect, warehouse_name, product, address="", balance=1):
    # добавляет id товара которого небыло ранее на складе
    cursor = connect.cursor()
    cursor.execute("INSERT INTO warehouse(warehouse_name, product, address, balance) VALUES"
                   " ({}, {}, '{}', {})".format(warehouse_name, product, address, balance))
    connect.commit()


@db_connect
def move_product_warehouse():
    # создает перемещение между складами
    pass


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
