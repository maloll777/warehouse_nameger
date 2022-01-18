from warehouse_DB import Warehouse

x = Warehouse()

if __name__ == '__main__':
    x.connect_db()
    x.warehouse_loop()
    x.close_db()
