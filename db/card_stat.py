from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.model import Base, session
from db.card import Card
from datetime import datetime


class CardStat(Base):
    __tablename__ = 'cards_stat'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    begin: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    open_card_count: Mapped[int] = mapped_column(nullable=False, default=0)
    add_to_cart_count: Mapped[int] = mapped_column(nullable=False, default=0)
    orders_count: Mapped[int] = mapped_column(nullable=False, default=0)
    orders_sum_rub: Mapped[float] = mapped_column(nullable=False, default=0)
    buyouts_count: Mapped[int] = mapped_column(nullable=False, default=0)
    buyouts_sum_rub: Mapped[float] = mapped_column(nullable=False, default=0)
    cancel_count: Mapped[int] = mapped_column(nullable=False, default=0)
    cancel_sum_rub: Mapped[float] = mapped_column(nullable=False, default=0)


def save(begin, end, card, open_card_count, add_to_cart_count, orders_count, orders_sum_rub, buyouts_count, buyouts_sum_rub, cancel_count, cancel_sum_rub):
    # Check if an card stat with the same card and begin exists
    obj = session.query(CardStat).filter_by(begin=begin, card=card).first()

    if obj:
        # Update existing card stat
        obj.end = end
        obj.open_card_count = open_card_count if open_card_count else 0
        obj.add_to_cart_count = add_to_cart_count if add_to_cart_count else 0
        obj.orders_count = orders_count if orders_count else 0
        obj.orders_sum_rub = orders_sum_rub if orders_sum_rub else 0
        obj.buyouts_count = buyouts_count if buyouts_count else 0
        obj.buyouts_sum_rub = buyouts_sum_rub if buyouts_sum_rub else 0
        obj.cancel_count = cancel_count if cancel_count else 0
        obj.cancel_sum_rub = cancel_sum_rub if cancel_sum_rub else 0
    else:
        # Create new card stat
        obj = CardStat(
            begin=begin,
            end=end,
            card=card,
            open_card_count=open_card_count,
            add_to_cart_count=add_to_cart_count,
            orders_count=orders_count,
            orders_sum_rub=orders_sum_rub,
            buyouts_count=buyouts_count,
            buyouts_sum_rub=buyouts_sum_rub,
            cancel_count=cancel_count,
            cancel_sum_rub=cancel_sum_rub
        )
        session.add(obj)
    session.commit()