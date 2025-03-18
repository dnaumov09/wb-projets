from datetime import datetime
from sqlalchemy import DateTime, Boolean

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session

from db.models.seller import Seller


SETTINGS_ID = 0


class Settings(Base):
    __tablename__ = 'settings'

    # seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'), nullable=False)
    # seller: Mapped[Seller] = relationship("Seller")

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, default=0)
    orders_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sales_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cards_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    adverts_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

#     load_cards_stat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
#     load_orders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
#     load_sales: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
#     adverts_stat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


# def get_settings(seller: Seller):
#     return session.query(Settings).filter(Settings.se == SETTINGS_ID).first()


# def save_settings(settings: Settings):
#     session.add(settings)
#     session.commit()


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