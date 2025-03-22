from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.model.seller import Seller
from db.util import camel_to_snake, save_records


class Card(Base):
    __tablename__ = 'cards'
    
    nm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    imt_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'), nullable=True)
    seller: Mapped[Seller] = relationship("Seller")


def get_seller_cards(seller_id) -> list[Card]:
    return session.query(Card).filter(Card.seller_id == seller_id).all()


def get_card_by_nm_id(nm_id) -> Card:
    return session.query(Card).filter(Card.nm_id == nm_id).first()


def save_cards(data, seller: Seller) -> list[Card]:
    data = [{camel_to_snake(k): v for k, v in item.items()} for item in data.get("cards", [])]
    return save_records(
        session=session,
        model=Card,
        data=data,
        key_fields=['nm_id']
        )