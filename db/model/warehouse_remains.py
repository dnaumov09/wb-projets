from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from sqlalchemy.schema import PrimaryKeyConstraint


from db.model.warehouse import Warehouse, check_warehouse
from db.model.remains import Remains
from db.model.seller import Seller
from db.model.card import Card
from db.util import camel_to_snake, save_records

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

    # def __init__(self, warehouse_id: int, warehouse: Warehouse, remains_id: int, remains: Remains, quantity: int):
    #     self.warehouse_id = warehouse_id
    #     self.warehouse = warehouse
    #     self.remains_id = remains_id
    #     self.remains = remains
    #     self.quantity = quantity


def save_warehouse_remains(data):
    result = save_records(
        session=session, 
        model=WarehouseRemains, 
        data=data, 
        key_fields=['warehouse_id', 'remains_id'])
    return result[0] + result[1]


    # wr_to_save = []
    # for item in data:
    #     warehouses = item.get('warehouses')
    #     for wh in warehouses:
    #         remains = next((r for r in db_remains if r.barcode == item.get('barcode')))
    #         warehouse = check_warehouse(wh.get('warehouseName'))
    #         q = wh.get('quantity')
    #         wr = WarehouseRemains(warehouse_id=warehouse.id, warehouse=warehouse, remains_id=remains.barcode, remains=remains, quantity=q)
    #         wr_to_save.append(wr)

    # session.bulk_save_objects(wr_to_save)
    # session.commit()
    
    # return wr_to_save
    

def get_warehouse_remains_by_seller_id(seller_id: int):
    return (
        session.query(WarehouseRemains)
            .join(Remains, Remains.barcode == WarehouseRemains.remains_id)
            .join(Card, Card.nm_id == Remains.nm_id)
            .join(Seller, Seller.id == Card.seller_id)
            .filter(Seller.id == seller_id).all()
    )