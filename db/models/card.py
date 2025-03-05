from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.models.seller import Seller


class Card(Base):
    __tablename__ = 'cards'
    
    nm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    imt_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'), nullable=True)
    seller: Mapped[Seller] = relationship("Seller")


    def __init__(self, nm_id, imt_id, title, vendor_code):
        self.nm_id = nm_id
        self.imt_id = imt_id
        self.title = title
        self.vendor_code = vendor_code
    

def save(item):
    session.add(item)
    session.commit()


def get_all() -> list[Card]:
    return session.query(Card).all()


def get_seller_cards(seller_id) -> list[Card]:
    return session.query(Card).filter(Card.seller_id == seller_id).all()


def get_by_nm_id(nm_id) -> Card:
    return session.query(Card).filter(Card.nm_id == nm_id).first()