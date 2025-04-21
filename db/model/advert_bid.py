from sqlalchemy import ForeignKey, Column, Integer, Float, Enum, and_
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import PrimaryKeyConstraint

import enum

from db.base import Base, session
from db.model.advert import Advert, AdvertType
from db.model.card import Card
from db.model.seller import Seller
from db.util import save_records


class BidType(enum.Enum):
    AUTOMATIC_CPM = 1
    SEARCH_CPM = 2
    CATALOG_CPM = 3


class AdvertBid(Base):
    __tablename__ = 'advert_bids'

    __table_args__ = (
        PrimaryKeyConstraint('advert_id', 'nm_id', 'bid_type'),
    )

    advert_id = Column(Integer, ForeignKey('adverts.advert_id'))
    advert = relationship("Advert")

    nm_id = Column(Integer, ForeignKey('cards.nm_id'))
    card = relationship("Card")

    bid_type = Column(Enum(BidType, native_enum=False))

    cpm = Column(Float)


def save_advert_bids(data) -> list[AdvertBid]:
    updated_data = []
    for advert in data:
        if advert['type'] == AdvertType.AUTOMATIC.value:
            for nm_cmp in advert['autoParams']['nmCPM']:
                updated_data.append({
                    'advert_id': advert['advertId'],
                    'nm_id': nm_cmp['nm'],
                    'cpm': nm_cmp['cpm'],
                    'bid_type': BidType.AUTOMATIC_CPM
                })
                    

        elif advert['type'] == AdvertType.AUCTION.value:
            for united_params in advert['unitedParams']:
                for nm_id in united_params['nms']:
                    updated_data.append({
                        'advert_id': advert['advertId'],
                        'nm_id': nm_id,
                        'cpm': united_params['searchCPM'],
                        'bid_type': BidType.SEARCH_CPM
                    })
                    updated_data.append({
                        'advert_id': advert['advertId'],
                        'nm_id': nm_id,
                        'cpm': united_params['catalogCPM'],
                        'bid_type': BidType.CATALOG_CPM
                    })
    
    return save_records(
        session=session,
        model=AdvertBid,
        data=updated_data,
        key_fields=['advert_id', 'nm_id', 'bid_type'])


def get_advert_bid(advert_id, nm_id) -> AdvertBid:
    return session.query(AdvertBid).filter(AdvertBid.advert_id != advert_id, AdvertBid.nm_id == nm_id).first()


def update_advert_bid(advert_bid: AdvertBid) -> AdvertBid:
    session.add(advert_bid)
    session.commit()