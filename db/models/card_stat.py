from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.models.card import Card
from db.models.seller import Seller
from datetime import datetime, time


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


def get_today_cards_stat_by_seller_id(seller_id):
    today_begin = datetime.combine(datetime.now().date(), time.min)
    return (
        session.query(CardStat)
        .join(CardStat.card)
        .filter(CardStat.begin == today_begin, Card.seller_id == seller_id)
        .all()
    )


def save_update_card_stat(data, now: datetime, seller: Seller) -> list[CardStat]:
    cards_stat_to_insert = []
    cards_stat_to_update = []

    existing_stat = {(cs.nm_id, cs.begin): cs for cs in get_today_cards_stat_by_seller_id(seller.id)}

    for item in data:
        nm_id = item.get("nmID")
        for day in item.get('history'):
            begin = datetime.strptime(day.get('dt'), "%Y-%m-%d")
            end = datetime.combine(begin, time.max) if begin < datetime.combine(now, time.min) else now
            
            stat_key = (nm_id, begin)
            if stat_key in existing_stat:
                card_stat = existing_stat[stat_key]
                card_stat.end = end
                card_stat.open_card_count = day.get('openCardCount', 0)
                card_stat.add_to_cart_count = day.get('addToCartCount')
                card_stat.orders_count = day.get('ordersCount')
                card_stat.orders_sum_rub = day.get('ordersSumRub')
                card_stat.buyouts_count = day.get('buyoutsCount', 0)
                card_stat.buyouts_sum_rub = day.get('buyoutsSumRub', 0)
                card_stat.cancel_count = day.get('cancelCount', 0)
                card_stat.cancel_sum_rub = day.get('cancelSumRub', 0)
                cards_stat_to_update.append(card_stat)
            else:
                card_stat = CardStat(
                    begin=begin,
                    end=end,
                    nm_id=nm_id,
                    open_card_count=day.get('openCardCount', 0),
                    add_to_cart_count=day.get('addToCartCount', 0),
                    orders_count=day.get('ordersCount', 0),
                    orders_sum_rub=day.get('ordersSumRub', 0),
                    buyouts_count=day.get('buyoutsCount', 0),
                    buyouts_sum_rub=day.get('buyoutsSumRub', 0),
                    cancel_count=day.get('cancelCount', 0),
                    cancel_sum_rub=day.get('cancelSumRub', 0)
                )
                cards_stat_to_insert.append(card_stat)

    # Bulk save for efficiency
    if cards_stat_to_insert:
        session.bulk_save_objects(cards_stat_to_insert)

    if cards_stat_to_update:
        session.bulk_save_objects(cards_stat_to_update)

    # Commit once for all operations
    session.commit()

    return cards_stat_to_insert + cards_stat_to_update