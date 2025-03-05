from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import PrimaryKeyConstraint

from db.base import Base, session
from db.models.card import Card
from db.models.warehouse import Warehouse


class Remains(Base):
    __tablename__ = 'remains'

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), primary_key=True, nullable=False)
    card: Mapped[Card] = relationship("Card")

    brand: Mapped[str] = mapped_column(nullable=False)
    subjectName: Mapped[str] = mapped_column(nullable=False)
    vendorCode: Mapped[str] = mapped_column(nullable=False)
    barcode: Mapped[str] = mapped_column(nullable=False)
    techSize: Mapped[str] = mapped_column(nullable=False)
    volume: Mapped[float] = mapped_column(nullable=False)
    inWayToClient: Mapped[int] = mapped_column(nullable=False)
    inWayFromClient: Mapped[int] = mapped_column(nullable=False)
    quantityWarehousesFull: Mapped[int] = mapped_column(nullable=False)

    def __init__(self, nm_id, brand, subjectName, vendorCode, barcode, techSize, volume, inWayToClient, inWayFromClient, quantityWarehousesFull):
        self.nm_id = nm_id
        self.brand = brand
        self.subjectName = subjectName
        self.vendorCode = vendorCode
        self.barcode = barcode
        self.techSize = techSize
        self.volume = volume
        self.inWayToClient = inWayToClient
        self.inWayFromClient = inWayFromClient
        self.quantityWarehousesFull = quantityWarehousesFull


def save_or_update_remains(card, brand, subjectName, vendorCode, barcode, techSize, volume, inWayToClient, inWayFromClient, quantityWarehousesFull) -> Remains:
    remains = session.query(Remains).filter(Remains.nm_id == card.nm_id).first()
    if remains:
        remains.brand = brand
        remains.subjectName = subjectName
        remains.vendorCode = vendorCode
        remains.barcode = barcode
        remains.techSize = techSize
        remains.volume = volume
        remains.inWayToClient = inWayToClient
        remains.inWayFromClient = inWayFromClient
        remains.quantityWarehousesFull = quantityWarehousesFull
    else:
        remains = Remains(card.nm_id, brand, subjectName, vendorCode, barcode, techSize, volume, inWayToClient, inWayFromClient, quantityWarehousesFull)
        session.add(remains)
    session.commit()
    return remains