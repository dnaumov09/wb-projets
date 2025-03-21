from sqlalchemy import ForeignKey, DateTime, Index, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.model.card import Card
from db.model.seller import Seller
from datetime import datetime, time


class CardStat(Base):
    __tablename__ = 'cards_stat'

    __table_args__ = (
        Index('idx_cards_stat_begin_nmid', 'begin', 'nm_id'),  # Composite index
    )

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


def save_card_stat(data, now: datetime, seller: Seller) -> list[CardStat]:
    existing_stat_list = session.scalars(select(CardStat).filter(
        CardStat.nm_id.in_([item.get("nmID") for item in data]),
        CardStat.begin.in_([datetime.strptime(h.get('dt'), "%Y-%m-%d") for item in data for h in item.get('history')])
    )).all()
    existing_stat = {(stat.nm_id, stat.begin): stat for stat in existing_stat_list}

    new_stat = []
    for item in data:
        nm_id = item.get("nmID")
        for day in item.get('history'):
            begin = datetime.strptime(day.get('dt'), "%Y-%m-%d")
            end = datetime.combine(begin, time.max) if begin < datetime.combine(now, time.min) else now
            stat_key = (nm_id, begin)
            is_existing = stat_key in existing_stat

            stat_fields = {
                "begin": begin,
                "end": end,
                "nm_id": nm_id,
                "open_card_count": day.get('openCardCount', 0),
                "add_to_cart_count": day.get('addToCartCount', 0),
                "orders_count": day.get('ordersCount', 0),
                "orders_sum_rub": day.get('ordersSumRub', 0),
                "buyouts_count": day.get('buyoutsCount', 0),
                "buyouts_sum_rub": day.get('buyoutsSumRub', 0),
                "cancel_count": day.get('cancelCount', 0),
                "cancel_sum_rub": day.get('cancelSumRub', 0)
            }

            existing_stat_output = []
            if is_existing:
                # Update existing advert
                stat = existing_stat[stat_key]
                for field, value in stat_fields.items():
                    setattr(stat, field, value)
                existing_stat_output.append(stat)
            else:
                # Collect for bulk insert
                new_stat.append(CardStat(**stat_fields))


    if new_stat:
        session.bulk_save_objects(new_stat)

    session.commit()
