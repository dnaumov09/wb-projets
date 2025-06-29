from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint


from db.model.card import get_cards
from db.util import camel_to_snake, convert_date, save_records
from db.base import Base

from admin.model import Seller
from admin.db_router import get_session


class Income(Base):
    __tablename__ = 'incomes'

    __table_args__ = (
        PrimaryKeyConstraint('income_id', 'nm_id'),
    )

    income_id = Column(Integer, nullable=False)
    number = Column(String)
    date = Column(DateTime)
    last_change_date = Column(DateTime)
    supplier_article = Column(String)
    tech_size = Column(String)
    barcode = Column(String, nullable=False)
    quantity = Column(Integer)
    total_price = Column(Float)
    date_close = Column(DateTime)
    warehouse_name = Column(String)

    nm_id = Column(Integer, ForeignKey('cards.nm_id'), nullable=False)
    card = relationship("Card")

    status = Column(String)

    buying_price = Column(Float, nullable=True, default=0)


def save_incomes(seller: Seller, data):
    data = [
        {camel_to_snake(k): v for k, v in item.items()}
        for item in data
    ]

    seller_nm_ids = [r.nm_id for r in get_cards(seller)]

    incomes_to_save = []
    for item in data:
        if item['nm_id'] not in seller_nm_ids:
            continue

        for field in ['date', 'last_change_date', 'date_close']:
            if field in item and isinstance(item[field], str):
                item[field] = convert_date(item[field], '%Y-%m-%dT%H:%M:%S')
        incomes_to_save.append(item)

    return save_records(
        session=get_session(seller),
        model=Income,
        data=incomes_to_save,
        key_fields=['income_id', 'barcode'])