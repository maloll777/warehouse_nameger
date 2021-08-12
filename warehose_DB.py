import psycopg2


def db_connect(func, *args) -> object:
    # декоратор для подключения к БД
    connect = psycopg2.connect(
        database="triol",
        user="postgres",
        password="",
        host="127.0.0.1",
        port="5432"
    )
    cursor = connect.cursor()

    def wrapper(*arg):
        return func(cursor, *arg)

    return wrapper


@db_connect
def find_code_product(cursor, id_product):
    # по id товара информацию о нем

    cursor.execute("select code_product, product_name, subgroup_product, group_product from product where "
                   "code_product = '{}';".format(id_product))
    return cursor.fetchall()

@db_connect
def add_product_whouse():
    # добавляет товар на склад
    pass

@db_connect
def remove_product_whouse():
    # удаляет товар со склада
    pass

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