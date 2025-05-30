import enum

from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, Enum, and_
from sqlalchemy.orm import relationship
from db.base import Base

from admin.model import Seller
from admin.db_router import get_session


class WeekDay(enum.Enum):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class AdvertSchedule(Base):
    __tablename__ = 'adverts_schedule'

    advert_id = Column(Integer, ForeignKey('adverts.advert_id'), primary_key=True)
    advert = relationship("Advert")

    weekday = Column(Enum(WeekDay, native_enum=False), primary_key=True)
    weekday_active = Column(Boolean, nullable=False)

    hours = Column(String)

    max_daily_budget = Column(Integer, nullable=False, default=0)


def get_advert_schedule(seller: Seller, advert_id: int, weekday: WeekDay) -> AdvertSchedule:
    return get_session(seller).query(AdvertSchedule).filter(
        and_(AdvertSchedule.advert_id == advert_id, AdvertSchedule.weekday == weekday)
    ).first()
