from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from db.base import Base, session
from db.model.card import Card
from db.model.seller import Seller
from db.util import save_records


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


def save_remains(data) -> list[Remains]:
    result = save_records(
        session=session,
        model=Remains,
        data=data,
        key_fields=['barcode'])
    return result[0] + result[1]


def get_remains_by_seller_id(seller_id: int) -> list[Remains]:
    return (
        session.query(Remains)
        .join(Remains.card).join(Card.seller)
        .filter(Card.seller_id == seller_id)
        .all()
    )


def get_remains_by_seller_id(seller_id: int) -> list[Remains]:
    return (
        session.query(Remains)
            .join(Card, Card.nm_id == Remains.nm_id)
            .join(Seller, Seller.id == Card.seller_id)
            .filter(Seller.id == seller_id).all()
    )