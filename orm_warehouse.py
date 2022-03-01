from peewee import SqliteDatabase, Model, DoesNotExist
from peewee import CharField, ForeignKeyField, IntegerField, FloatField, BooleanField

db = SqliteDatabase('./warehouse_sqlite_id.db')


class Table(Model):
    class Meta:
        database = db


class ProductBrand(Table):
    brand_name = CharField()


class ProductGroup(Table):
    group_name = CharField()


class ProductSubGroup(Table):
    subgroup_name = CharField()


class DocumentType(Table):
    doc_type_id = CharField()


class Product(Table):
    # таблица описана не полностью
    product_name = CharField()
    price = FloatField()
    ean_code = IntegerField()
    code_product = CharField()
    description = CharField()
    group_product = ForeignKeyField(ProductGroup)
    subgroup_product = ForeignKeyField(ProductSubGroup)
    brand_product = ForeignKeyField(ProductBrand)


class Warehouse_list(Table):
    warehouse_name = CharField()
    warehouse_address = CharField()


class Operation_doc_warehouse(Table):
    create_date = CharField()
    move_date = CharField()
    doc_status = CharField()
    doc_type_id = ForeignKeyField(DocumentType)
    comment_operation = CharField()
    doc_number = CharField()


class Product_move(Table):
    product_id = ForeignKeyField(Product)
    doc_operation_id = ForeignKeyField(Operation_doc_warehouse)
    warehouse_out_id = ForeignKeyField(Warehouse_list)
    warehouse_in_id = ForeignKeyField(Warehouse_list)
    count = IntegerField()


class Reserve(Table):
    product_id = ForeignKeyField(Product)
    balance = IntegerField()
    ship = BooleanField()
    doc_operation_id = ForeignKeyField(Operation_doc_warehouse)


class Warehouse(Table):
    product_id = ForeignKeyField(Product)
    address = CharField()
    warehouse_id = ForeignKeyField(Warehouse_list)
    balance = IntegerField()
