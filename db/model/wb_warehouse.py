from sqlalchemy import Column, Integer, String, Boolean
from db.base import Base, session

from db.util import camel_to_snake, save_records

class WBWarehouse(Base):
    __tablename__ = 'wb_warehouses'

    id = Column(Integer, primary_key=True)
    name = Column(String) 
    address = Column(String) 
    work_time = Column(String) 
    accepts_qr = Column(Boolean) 
    is_active = Column(Boolean) 


def save_wb_warehouses(data) -> list[WBWarehouse]:
    data = [{camel_to_snake(k): v for k, v in item.items()} for item in data]
    return save_records(
        session=session,
        model=WBWarehouse,
        data=data,
        key_fields=['id']
        )