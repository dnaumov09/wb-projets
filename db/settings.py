from datetime import datetime
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped, mapped_column
from db.model import Base, session


class Settings(Base):
    __tablename__ = 'settings'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, last_updated):  
        self.last_updated = last_updated


def get_settings():
    settings = session.query(Settings).first()
    if settings is None:
        settings = Settings(last_updated=datetime.now())
        session.add(settings)
        session.commit()
    return settings


def save_settings(settings):
    session.add(settings)
    session.commit()


# def update_settings(last_updated):
#     session.query(Settings).filter(Settings.id == 0).update({Settings.last_updated: last_updated})
#     session.commit()