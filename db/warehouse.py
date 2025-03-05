from sqlalchemy.orm import Mapped, mapped_column
from db.model import Base, session

class Warehouse(Base):
    __tablename__ = 'warehouses'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()


def check_warehouse(name) -> Warehouse:
    warehouse = session.query(Warehouse).filter_by(name=name).first()
    if not warehouse:
        warehouse = Warehouse(name=name)
        session.add(warehouse)
        session.commit()
    return warehouse