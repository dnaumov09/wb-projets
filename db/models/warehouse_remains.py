from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from sqlalchemy.schema import PrimaryKeyConstraint


from db.models.warehouse import Warehouse, check_warehouse
from db.models.remains import Remains
from db.models.seller import Seller
from db.models.card import Card

class WarehouseRemains(Base):
    __tablename__ = 'warehouse_remains'

    __table_args__ = (
        PrimaryKeyConstraint('warehouse_id', 'remains_id'),
    )

    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), primary_key=True, nullable=False)
    warehouse: Mapped[Warehouse] = relationship("Warehouse")

    remains_id: Mapped[str] = mapped_column(ForeignKey('remains.barcode'), primary_key=True, nullable=False)
    remains: Mapped[Remains] = relationship("Remains")

    quantity: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, warehouse_id: int, warehouse: Warehouse, remains_id: int, remains: Remains, quantity: int):
        self.warehouse_id = warehouse_id
        self.warehouse = warehouse
        self.remains_id = remains_id
        self.remains = remains
        self.quantity = quantity


def save_warehouse_remains(data, db_warehouses: list[Warehouse], db_remains: list[Remains]):
    wr_to_save = []
    for item in data:
        warehouses = item.get('warehouses')
        for wh in warehouses:
            remains = next((r for r in db_remains if r.barcode == item.get('barcode')), None)
            warehouse = check_warehouse(wh.get('warehouseName'))
            q = wh.get('quantity')
            wr = WarehouseRemains(warehouse_id=warehouse.id, warehouse=warehouse, remains_id=remains.barcode, remains=remains, quantity=q)
            wr_to_save.append(wr)

    session.bulk_save_objects(wr_to_save)
    session.commit()

def find_or_create_warehouse_remains(warehouse: Warehouse, remains: Remains, quantity: int) -> WarehouseRemains:
    warehouse_remains = session.query(WarehouseRemains).filter(WarehouseRemains.warehouse_id == warehouse.id, WarehouseRemains.remains_id == remains.barcode).first()
   
    if warehouse_remains:
        warehouse_remains.quantity = quantity
    if not warehouse_remains:
        warehouse_remains = WarehouseRemains(warehouse.id, warehouse, remains.barcode, remains, quantity)
    
    return warehouse_remains


def save_warehouse_remains_list(warehouse_remains_list: list[WarehouseRemains]):
    session.bulk_save_objects(warehouse_remains_list)
    session.commit()
    

def get_warehouse_remains_by_seller_id(seller_id: int):
    return (
        session.query(WarehouseRemains)
            .join(Remains, Remains.barcode == WarehouseRemains.remains_id)
            .join(Card, Card.nm_id == Remains.nm_id)
            .join(Seller, Seller.id == Card.seller_id)
            .filter(Seller.id == seller_id).all()
    )