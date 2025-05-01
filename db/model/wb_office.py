from sqlalchemy import Column, Integer, String, Float, Boolean

from db.util import camel_to_snake, save_records
from db.model.seller import Seller
from db.base import Base

from admin.db_router import get_session


class WBOffices(Base):
    __tablename__ = 'wb_offices'

    id = Column(Integer, primary_key=True)
    address = Column(String)  
    name = Column(String)  
    city = Column(String) 
    longitude = Column(Float)
    latitude = Column(Float)
    cargo_type = Column(Integer) #Тип товара, который принимает склад: 1 - стандартный, 2 - СГТ (Сверхгабаритный товар), 3 - КГТ+ (Крупногабаритный товар)
    delivery_type = Column(Integer) #Тип доставки, который принимает склад: 1 - доставка на склад WB, 2 - доставка силами продавца, 3 - доставка курьером WB
    selected = Column(Boolean)


def save_wb_offices(seller: Seller, data) -> list[WBOffices]:
    data = [{camel_to_snake(k): v for k, v in item.items()} for item in data]
    return save_records(
        session=get_session(seller),
        model=WBOffices,
        data=data,
        key_fields=['id']
        )