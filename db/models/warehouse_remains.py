from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from sqlalchemy.schema import PrimaryKeyConstraint


from db.models.warehouse import Warehouse
from db.models.remains import Remains

class WarehouseRemains(Base):
    __tablename__ = 'warehouse_remains'

    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), primary_key=True, nullable=False)
    remains_id: Mapped[int] = mapped_column(ForeignKey('remains.nm_id'), primary_key=True, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('warehouse_id', 'remains_id'),
    )

    warehouse: Mapped[Warehouse] = relationship("Warehouse")
    remain: Mapped[Remains] = relationship("Remains")

    quantity: Mapped[int] = mapped_column(nullable=True)

    def __init__(self, warehouse_id, remains_id):
        self.warehouse_id = warehouse_id
        self.remains_id = remains_id


def check_warehouse_remains(warehouse_id: int, remains_id: int) -> WarehouseRemains:
    warehouse_remains = session.query(WarehouseRemains).filter(WarehouseRemains.warehouse_id == warehouse_id, WarehouseRemains.remains_id == remains_id).first()
    
    if not warehouse_remains:
        warehouse_remains = WarehouseRemains(warehouse_id, remains_id)
        session.add(warehouse_remains)
        session.commit()
    
    return warehouse_remains


def update_warehouse_remains(warehouse_remains: WarehouseRemains, quantity: int):
    warehouse_remains.quantity = quantity
    session.add(warehouse_remains)
    session.commit()