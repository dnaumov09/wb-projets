from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.models.seller import Seller

class User(Base):
    __tablename__ = 'users'

    tg_chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(nullable=False)
    receive_orders: Mapped[bool] = mapped_column(nullable=False)

    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'), nullable=True)
    id: Mapped[Seller] = relationship("Seller")


def get_user(chat_id: int) -> User:
    return session.query(User).get(chat_id)


def get_admins() -> list[User]:
    return session.query(User).all()