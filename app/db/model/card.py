from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.util import camel_to_snake, save_records

from admin.model import Seller
from admin.db_router import get_session

class Card(Base):
    __tablename__ = 'cards'
    
    nm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    imt_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=True)


def get_cards(seller: Seller) -> list[Card]:
    return get_session(seller).query(Card).all()


def get_card_by_nm_id(seller: Seller, nm_id) -> Card:
    return get_session(seller).query(Card).filter(Card.nm_id == nm_id).first()


def save_cards(seller: Seller, data) -> list[Card]:
    data = [
        {**{camel_to_snake(k): v for k, v in item.items()}}
        for item in data.get("cards", [])
    ]

    return save_records(
        session=get_session(seller),
        model=Card,
        data=data,
        key_fields=['nm_id']
        )