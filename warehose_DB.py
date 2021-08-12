import psycopg2


def db_connect(func):
    # декоратор для подключения к БД
    connect = psycopg2.connect(
        database="triol",
        user="postgres",
        password="",
        host="127.0.0.1",
        port="5432"
    )

    def wrapper():
        return func(connect)

    return wrapper
