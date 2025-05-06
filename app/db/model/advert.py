import logging
from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, select, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from admin.model import Seller
from admin.db_router import get_session

class AdvertType(Enum):
    IN_CATALOG = 4
    IN_CONTENT = 5
    IN_SEARCH = 6
    IN_MAIN_PAGE_RECOMENDATIONS = 7
    AUTOMATIC = 8
    AUCTION = 9

class Status(Enum):
    DELETING = -1
    READY = 4
    COMPLETED = 7
    DECLINED = 8
    ONGOING = 9
    PAUSED = 11


class PaymentType(Enum):
    CPM = 'cpm'
    CPO = 'cpo'
    UNDEFINED = ''


class Advert(Base):
    __tablename__ = 'adverts'

    advert_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)

    create_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    change_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    daily_budget: Mapped[float] = mapped_column(nullable=False)
    search_pluse_state: Mapped[bool] = mapped_column(nullable=True)

    advert_type: Mapped[AdvertType] = mapped_column(PgEnum(AdvertType, native_enum=False), nullable=False)
    status: Mapped[Status] = mapped_column(PgEnum(Status, native_enum=False), nullable=False) # -1 - кампания в процессе удаления, 4 - готова к запуску, 7 - кампания завершена, 8 - отказался, 9 - идут показы, 11 - кампания на паузе
    payment_type: Mapped[PaymentType] = mapped_column(PgEnum(PaymentType, native_enum=False), nullable=False)


def parse_datetime(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')) if dt_str else None


def get_adverts_by_seller(seller: Seller):
    return get_session(seller).query(Advert).all()


def save_adverts(seller: Seller, data) -> list[Advert]:
    # Fetch all existing advert IDs from the database
    existing_adverts_list = get_session(seller).scalars(select(Advert)).all()
    existing_adverts = {adv.advert_id: adv for adv in existing_adverts_list}
    
    # List of adverts that exist in DB but not in incoming data -> to archive
    existing_advert_ids = set(existing_adverts.keys())
    incoming_advert_ids = {ad['advertId'] for ad in data}
    adverts_to_archive = list(existing_advert_ids - incoming_advert_ids)

    new_adverts = []
    existing_adverts_output = []
    for advert_data in data:
        advert_id = advert_data['advertId']
        is_existing = advert_id in existing_adverts

        advert_fields = {
            'advert_id': advert_id,
            'create_time': parse_datetime(advert_data.get('createTime')),
            'start_time': parse_datetime(advert_data.get('startTime')),
            'end_time': parse_datetime(advert_data.get('endTime')),
            'change_time': parse_datetime(advert_data.get('changeTime')),
            'name': advert_data.get('name', ''),
            'daily_budget': advert_data.get('dailyBudget', 0.0),
            'status': Status(advert_data.get('status')),
            'advert_type': AdvertType(advert_data.get('type')),
            'payment_type': PaymentType(advert_data.get('paymentType')),
            'seller_id': seller.id,
            'search_pluse_state': advert_data.get('searchPluseState', None)
        }

        if is_existing:
            # Update existing advert
            advert = existing_adverts[advert_id]
            for field, value in advert_fields.items():
                setattr(advert, field, value)
            existing_adverts_output.append(advert)
        else:
            # Collect for bulk insert
            new_adverts.append(Advert(**advert_fields))

    session = get_session(seller)
    if new_adverts:
        session.bulk_save_objects(new_adverts)

    session.commit()

    if adverts_to_archive:
        logging.info(f"[{seller.trade_mark}] Adverts to archive (missing in incoming data):")
        logging.info(f"{adverts_to_archive}")

    return new_adverts + existing_adverts_output
