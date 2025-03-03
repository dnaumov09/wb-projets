from sqlalchemy.orm import Mapped, mapped_column
from db.model import Base, session

class User(Base):
    __tablename__ = 'users'

    tg_chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column()
    receive_orders: Mapped[bool] = mapped_column()


def get_user(chat_id: int) -> User:
    return session.query(User).get(chat_id)


def get_admins() -> list[User]:
    return session.query(User).all()