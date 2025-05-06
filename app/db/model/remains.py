from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model.card import Card
from db.util import save_records
from db.base import Base

from admin.model import Seller
from admin.db_router import get_session


class Remains(Base):
    __tablename__ = 'remains'

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    brand: Mapped[str] = mapped_column(nullable=False)
    subject_name: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=False)
    barcode: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    tech_size: Mapped[str] = mapped_column(nullable=False)
    volume: Mapped[float] = mapped_column(nullable=False)
    in_way_to_client: Mapped[int] = mapped_column(nullable=True)
    in_way_from_client: Mapped[int] = mapped_column(nullable=True)
    quantity_warehouses_full: Mapped[int] = mapped_column(nullable=True)


def save_remains(seller: Seller, data) -> list[Remains]:
    result = save_records(
        session=get_session(seller),
        model=Remains,
        data=data,
        key_fields=['barcode'])
    return result[0] + result[1]


def get_remains_by_seller(seller: Seller) -> list[Remains]:
    return (
        get_session(seller).query(Remains)
        .join(Remains.card).join(Card.seller)
        .filter(Card.seller_id == seller.id)
        .all()
    )
