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

    def wrapper(*args):
        return func(cursor, *args)

    return wrapper


@db_connect
def find_code_product(cursor, id_product):
    # ищет по id товара информацию о нем

    cursor.execute("select code_product, product_name, subgroup_product, group_product from product where "
                   "code_product = '{}';".format(id_product))
    return cursor.fetchall()

