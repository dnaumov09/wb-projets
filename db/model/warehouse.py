from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, session

class Warehouse(Base):
    __tablename__ = 'warehouses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()

    def __init__(self, name):
        self.name = name


def check_warehouse(name):
    wh = session.query(Warehouse).filter(Warehouse.name == name).first()

    if wh is None:
        wh = Warehouse(name=name)
        session.add(wh)
        session.commit()
    
    return wh


def get_warehouses():
    return session.query(Warehouse).all()