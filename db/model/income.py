from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, select
from sqlalchemy.orm import relationship

from db.base import Base, session

from db.model.seller import Seller
from util import camel_to_snake, convert_date, get_existing_records, save_records


class Income(Base):
    __tablename__ = 'incomes'

    income_id = Column(Integer, primary_key=True, index=True)
    number = Column(String)
    date = Column(DateTime)
    last_change_date = Column(DateTime)
    supplier_article = Column(String)
    tech_size = Column(String)
    barcode = Column(String)
    quantity = Column(Integer)
    total_price = Column(Float)
    date_close = Column(DateTime)
    warehouse_name = Column(String)

    nm_id = Column(Integer, ForeignKey('cards.nm_id'), nullable=False)
    card = relationship("Card")

    seller_id = Column(Integer, ForeignKey('sellers.id'))
    seller = relationship("Seller")

    status = Column(String)


def save_incomes(data, seller: Seller):
    data = {camel_to_snake(k): v for k, v in data.items()}

    for field in ['date', 'last_change_date', 'date_close']:
        if field in data and isinstance(data[field], str):
            data[field] = convert_date(data[field], '%Y-%m-%dT%H:%M:%S')
        data['sellet_id'] = seller.id

    return save_records(
        session=session,
        model=Income,
        data=data,
        key_fields=['income_id'])