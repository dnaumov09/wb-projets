from datetime import datetime
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.model import Base, session

from db.card import Card


class Pipeline(Base):
    __tablename__ = 'pipeline'

    id: Mapped[int] = mapped_column(primary_key=True)

    card_nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    begin_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    open_card_count: Mapped[int] = mapped_column(nullable=False)
    add_to_cart_count: Mapped[int] = mapped_column(nullable=False)
    orders_count: Mapped[int] = mapped_column(nullable=False)
    orders_sum_rub: Mapped[float] = mapped_column(nullable=False)
    buyouts_count: Mapped[int] = mapped_column(nullable=False)
    buyouts_sum_rub: Mapped[float] = mapped_column(nullable=False)
    cancel_count: Mapped[int] = mapped_column(nullable=False)
    cancel_sum_rub: Mapped[float] = mapped_column(nullable=False)

    
    def __init__(self, card, begin_date, end_date, open_card_count, add_to_cart_count, orders_count, orders_sum_rub, buyouts_count, buyouts_sum_rub, cancel_count, cancel_sum_rub):
        self.card = card
        self.begin_date = begin_date
        self.end_date = end_date
        self.open_card_count = open_card_count
        self.add_to_cart_count = add_to_cart_count
        self.orders_count = orders_count
        self.orders_sum_rub = orders_sum_rub
        self.buyouts_count = buyouts_count
        self.buyouts_sum_rub = buyouts_sum_rub
        self.cancel_count = cancel_count
        self.cancel_sum_rub = cancel_sum_rub


def save(pipeline: Pipeline):
    db_pipeline = session.query(Pipeline).filter_by(card=pipeline.card, begin_date=pipeline.begin_date).first()
    if db_pipeline:
        db_pipeline.end_date = pipeline.end_date
        db_pipeline.open_card_count = pipeline.open_card_count
        db_pipeline.add_to_cart_count = pipeline.add_to_cart_count
        db_pipeline.orders_count = pipeline.orders_count
        db_pipeline.orders_sum_rub = pipeline.orders_sum_rub
        db_pipeline.buyouts_count = pipeline.buyouts_count
        db_pipeline.buyouts_sum_rub = pipeline.buyouts_sum_rub
        db_pipeline.cancel_count = pipeline.cancel_count
        db_pipeline.cancel_sum_rub = pipeline.cancel_sum_rub
        session.add(db_pipeline)
    else:
        session.add(pipeline)
    
    session.commit()