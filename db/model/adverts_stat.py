from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, DateTime, Index, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.model.card import Card
from db.model.advert import Advert


class AppType(Enum):
    WEBSITE = 1
    IOS = 32
    ANDROID = 64


class AdvertsStat(Base):
    __tablename__ = 'adverts_stat'

    __table_args__ = (
        Index('idx_adverts_stat_date_advertid_nmid_apptype', 'date', 'advert_id', 'nm_id', 'app_type'),  # Composite index
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    advert_id: Mapped[int] = mapped_column(ForeignKey('adverts.advert_id'), nullable=False)
    advert: Mapped[Advert] = relationship("Advert")

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    sum: Mapped[float] = mapped_column(nullable=False)          # Затраты, ₽.
    views: Mapped[int] = mapped_column(nullable=False)          # Количество просмотров
    clicks: Mapped[int] = mapped_column(nullable=False)         # Количество кликов
    atbs: Mapped[int] = mapped_column(nullable=False)           # Количество добавлений товаров в корзину
    orders: Mapped[int] = mapped_column(nullable=False)         # Количество заказов
    shks: Mapped[int] = mapped_column(nullable=False)           # Количество заказанных товаров, шт.
    sum_price: Mapped[float] = mapped_column(nullable=False)    # Заказов на сумму, ₽.
    app_type: Mapped[AppType] = mapped_column(nullable=False)   #Тип платформы (1 - сайт, 32 - Android, 64 - IOS)


class BoosterStat(Base):
    __tablename__ = 'boosters_stat'

    __table_args__ = (
        Index('idx_boosters_stat_date_advertid_nmid', 'date', 'advert_id', 'nm_id'),  # Composite index
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    advert_id: Mapped[int] = mapped_column(ForeignKey('adverts.advert_id'), nullable=False)
    advert: Mapped[Advert] = relationship("Advert")

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    avg_position: Mapped[int] = mapped_column(nullable=False)
    

def get_existing_stat(data):
    advert_ids = []
    dates = []
    app_types = []
    nm_ids = []
    for advert in data:
        advert_ids.append(advert.get('advertId'))
        for day in advert.get('days', []):
            dates.append(datetime.fromisoformat(day.get('date')).replace(tzinfo=None))
            for app in day.get('apps', []):
                app_types.append(AppType(app.get('appType')))
                for nm in app.get('nm', []):
                    nm_ids.append(nm.get('nmId'))

    advert_ids = list(set(advert_ids))
    dates = list(set(dates))
    app_types = list(set(app_types))
    nm_ids = list(set(nm_ids))
    
    existing_stat_list = session.scalars(select(AdvertsStat).filter(
            AdvertsStat.advert_id.in_(advert_ids),
            AdvertsStat.date.in_(dates),
            AdvertsStat.app_type.in_(app_types),
            AdvertsStat.nm_id.in_(nm_ids)
        )).all()
    return {(stat.advert_id, stat.date, stat.app_type, stat.nm_id): stat for stat in existing_stat_list}


def get_existing_booster_stat(data):
    advert_ids = []
    dates = []
    nm_ids = []
    for advert in data:
        advert_ids.append(advert.get('advertId'))
        for bs in advert.get('boosterStats', []):
            dates.append(datetime.fromisoformat(bs.get('date')).replace(tzinfo=None))
            nm_ids.append(bs.get('nm'))

    advert_ids = list(set(advert_ids))
    dates = list(set(dates))
    nm_ids = list(set(nm_ids))
    
    existing_stat_list = session.scalars(select(BoosterStat).filter(
            BoosterStat.advert_id.in_(advert_ids),
            BoosterStat.date.in_(dates),
            BoosterStat.nm_id.in_(nm_ids)
        )).all()
    return {(stat.advert_id, stat.date, stat.nm_id): stat for stat in existing_stat_list}


def parse_adverts_stat(advert, existing_stat):
    new_stat = []
    existing_stat_output = []
    advert_id = advert.get('advertId')
    for day in advert.get('days'):
        date = datetime.fromisoformat(day.get('date')).replace(tzinfo=None)
        for app in day.get('apps'):
            app_type = AppType(app.get('appType'))
            for nm in app.get('nm'):
                nm_id = nm.get('nmId')
                stat_key = (advert_id, date, app_type, nm_id)
                is_existing = stat_key in existing_stat

                advert_stat_fields = {
                    'advert_id': advert_id,
                    'date': date,
                    'app_type': app_type,
                    'nm_id': nm_id,
                    'sum': nm.get('sum'),
                    'views': nm.get('views'),
                    'clicks': nm.get('clicks'),
                    'atbs': nm.get('atbs'),
                    'orders': nm.get('orders'),
                    'shks': nm.get('shks'),
                    'sum_price': nm.get('sum_price'),
                }
                if is_existing:
                    stat = existing_stat[stat_key]
                    for field, value in advert_stat_fields.items():
                        setattr(stat, field, value)
                    existing_stat_output.append(stat)
                else:
                    new_stat.append(AdvertsStat(**advert_stat_fields))
    return new_stat, existing_stat_output


def parse_booster_stat(advert, existing_booster_stat):
    new_booster_stat = []
    existing_booster_stat_output = []
    booster_stats = advert.get('boosterStats')
    if booster_stats:
        advert_id = advert.get('advertId')
        for booster_stat in booster_stats:
            date = datetime.fromisoformat(booster_stat.get('date').replace('Z', '+00:00')).replace(tzinfo=None)
            nm_id = booster_stat.get('nm')
            stat_key = (advert_id, date, nm_id)
            is_existing = stat_key in existing_booster_stat

            booster_stat_fields = {
                'advert_id': advert_id,
                'date': date,
                'nm_id': nm_id,
                'avg_position': booster_stat.get('avg_position')
            }

            if is_existing:
                stat = existing_booster_stat[stat_key]
                for field, value in booster_stat_fields.items():
                    setattr(stat, field, value)
                existing_booster_stat_output.append(stat)

    return new_booster_stat, existing_booster_stat_output


def save_adverts_stat(data):
    existing_stat = get_existing_stat(data)
    existing_booster_stat = get_existing_booster_stat(data)
    
    new_stat = []
    existing_stat_output = []
    new_booster_stat = []
    existing_booster_stat_output = []
    for advert in data:
        advert_new_stat, advert_existing_stat_output = parse_adverts_stat(advert, existing_stat)
        new_stat.extend(advert_new_stat)
        existing_stat_output.extend(advert_existing_stat_output)

        advert_new_booster_stat, advert_existing_booster_stat_output = parse_booster_stat(advert, existing_booster_stat)
        new_booster_stat.extend(advert_new_booster_stat)
        existing_booster_stat_output.extend(advert_existing_booster_stat_output)

    if new_stat:
        session.bulk_save_objects(new_stat)

    if new_booster_stat:
        session.bulk_save_objects(new_booster_stat)

    session.commit()
    return new_stat + existing_stat_output, new_booster_stat + existing_booster_stat_output