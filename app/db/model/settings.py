from datetime import datetime
from sqlalchemy import DateTime, Boolean, String

from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

from admin.model import Seller
from admin.db_router import get_session



class SellerSettings(Base):
    __tablename__ = 'seller_settings'

    sid: Mapped[bool] = mapped_column(String, nullable=False, primary_key=True)

    load_cards_stat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cards_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    load_orders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    orders_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    load_sales: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sales_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    load_adverts_stat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    adverts_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    keywords_stat_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    load_finances: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    finances_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    load_remains: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    load_imcomes: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    incomes_last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    update_pipeline_data: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


def get_seller_settings(seller: Seller):
    return get_session(seller).query(SellerSettings).first()


def save_settings(seller: Seller, settings: SellerSettings):
    session = get_session(seller)
    session.add(settings)
    session.commit()