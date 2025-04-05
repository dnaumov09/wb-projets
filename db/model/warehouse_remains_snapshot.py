from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import PrimaryKeyConstraint


from db.base import Base, session
from db.model.warehouse import Warehouse
from db.model.warehouse_remains import WarehouseRemains
from db.model.remains import Remains


class WarehouseRemainsSnapshot(Base):
    __tablename__ = 'warehouse_remains_snapshot'

    warehouse_id: Mapped[int] = mapped_column(ForeignKey('warehouses.id'), primary_key=True, nullable=False)
    warehouse: Mapped[Warehouse] = relationship("Warehouse")

    remains_id: Mapped[str] = mapped_column(ForeignKey('remains.barcode'), primary_key=True, nullable=False)
    remains: Mapped[Remains] = relationship("Remains")

    quantity: Mapped[int] = mapped_column(nullable=True)

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, primary_key=True)

    def __init__(self, warehouse_id, remains_id, quantity, date):
        self.warehouse_id = warehouse_id
        self.remains_id = remains_id
        self.quantity = quantity
        self.date = date


def save_remains_snapshot(remains: list[WarehouseRemains]) -> list[WarehouseRemainsSnapshot]:
    """Save a snapshot of WarehouseRemains at midnight (00:00) for the current day."""
    snapshot_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Prepare a list of dictionaries for bulk_insert_mappings
    snapshots_data = [
        {
            "warehouse_id": r.warehouse_id,
            "remains_id": r.remains_id,
            "quantity": r.quantity,
            "date": snapshot_date
        }
        for r in remains
    ]

    session.bulk_insert_mappings(WarehouseRemainsSnapshot, snapshots_data)
    session.commit()
