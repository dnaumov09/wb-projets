from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, session


class Seller(Base):
    __tablename__ = 'sellers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    token: Mapped[str] = mapped_column(nullable=False)
    sid: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    trade_mark: Mapped[str] = mapped_column(nullable=True)


def update_seller_data(token: str, sid: str, name: str, trade_mark: str):
    session.query(Seller).filter_by(token=token).update({'sid': sid, 'name': name, 'trade_mark': trade_mark})
    session.commit()


def get_seller(id: int):
    return session.query(Seller).filter_by(id=id).first()