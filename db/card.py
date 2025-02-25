from sqlalchemy.orm import Mapped, mapped_column
from db.model import Base, session


class Card(Base):
    __tablename__ = 'cards'
    
    nm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    imt_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=True)


    def __init__(self, nm_id, imt_id, title, vendor_code):
        self.nm_id = nm_id
        self.imt_id = imt_id
        self.title = title
        self.vendor_code = vendor_code
    

def save(item):
    session.add(item)
    session.commit()


def get_all():
    return session.query(Card).all()