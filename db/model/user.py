from sqlalchemy import ForeignKey, Column, String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.model.seller import Seller

class User(Base):
    __tablename__ = 'users'

    tg_chat_id = Column(Integer, primary_key=True, autoincrement=False)  
    name = Column(String, nullable=False) 
    receive_orders = Column(Boolean, nullable=False, default=False)
    receive_supplies_info = Column(Boolean, nullable=True, default=False)

    seller_id = Column(Integer, ForeignKey('sellers.id'), nullable=True)
    seller = relationship("Seller")


def get_user(chat_id: int) -> User:
    return session.query(User).get(chat_id)


def get_admins() -> list[User]:
    return session.query(User).all()


def get_seller_users(seller: Seller):
    return session.query(User).where(User.seller_id == seller.id).all()