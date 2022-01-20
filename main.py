from warehouse_DB import WarehouseConsole

x = WarehouseConsole()

if __name__ == '__main__':
    x.connect_db()
    x.warehouse_loop()
    x.close_db()
