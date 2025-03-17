from datetime import datetime
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, session


SETTINGS_ID = 0


class Settings(Base):
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, default=0)
    orders_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sales_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cards_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    adverts_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def get_orders_last_updated():
    settings = session.query(Settings).filter(Settings.id == SETTINGS_ID).first()
    return settings.orders_last_updated


def set_orders_last_updated(last_updated):
    session.query(Settings).filter(Settings.id == SETTINGS_ID).update({Settings.orders_last_updated: last_updated})
    session.commit()


def get_sales_last_updated():
    settings = session.query(Settings).filter(Settings.id == SETTINGS_ID).first()
    return settings.sales_last_updated


def set_sales_last_updated(last_updated):
    session.query(Settings).filter(Settings.id == SETTINGS_ID).update({Settings.sales_last_updated: last_updated})
    session.commit()


def get_sales_last_updated():
    settings = session.query(Settings).filter(Settings.id == SETTINGS_ID).first()
    return settings.sales_last_updated


def set_cards_stat_last_updated(last_updated):
    session.query(Settings).filter(Settings.id == SETTINGS_ID).update({Settings.cards_stat_last_updated: last_updated})
    session.commit()


def get_cards_stat_last_updated():
    settings = session.query(Settings).filter(Settings.id == SETTINGS_ID).first()
    return settings.cards_stat_last_updated


def set_adverts_stat_last_updated(last_updated):
    session.query(Settings).filter(Settings.id == SETTINGS_ID).update({Settings.adverts_stat_last_updated: last_updated})
    session.commit()


def get_adverts_stat_last_updated():
    settings = session.query(Settings).filter(Settings.id == SETTINGS_ID).first()
    return settings.adverts_stat_last_updated