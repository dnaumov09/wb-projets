from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import PrimaryKeyConstraint

from db.model.warehouse import Warehouse
from db.model.remains import Remains
from db.model.card import Card
from db.util import save_records
from db.base import Base

from admin.model import Seller
from admin.db_router import get_session


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


def save_warehouse_remains(seller: Seller, data):
    result = save_records(
        session=get_session(seller), 
        model=WarehouseRemains, 
        data=data, 
        key_fields=['warehouse_id', 'remains_id'])
    return result[0] + result[1]


def get_warehouse_remains(seller: Seller):
    return get_session(seller).query(WarehouseRemains).all()