from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.model.seller import Seller
from util import camel_to_snake, convert_date, save_records


class Card(Base):
    __tablename__ = 'cards'
    
    nm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    imt_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey('sellers.id'), nullable=True)
    seller: Mapped[Seller] = relationship("Seller")


def get_seller_cards(seller_id) -> list[Card]:
    return session.query(Card).filter(Card.seller_id == seller_id).all()


def get_card_by_nm_id(nm_id) -> Card:
    return session.query(Card).filter(Card.nm_id == nm_id).first()


#TODO UPDATE IT!!!!!!
def save_cards(data, seller: Seller) -> list[Card]:
    data = [{camel_to_snake(k): v for k, v in item.items()} for item in data.get("cards", [])]
    return save_records(
        session=session,
        model=Card,
        data=data,
        key_fields=['nm_id']
        )

    # cards_to_insert = []
    # cards_to_update = []

    # existing_cards = {card.nm_id: card for card in get_seller_cards(seller.id)}

    # for item in data.get('cards'):
    #     nm_id = item.get('nmID')
    #     if nm_id in existing_cards:
    #         # Update existing card
    #         card = existing_cards[nm_id]
    #         card.imt_id = item.get('imtID')
    #         card.title = item.get('title')
    #         card.vendor_code = item.get('vendorCode')
    #         cards_to_update.append(card)
    #     else:
    #         # Create new card
    #         card = Card(
    #             nm_id=nm_id,
    #             imt_id=item.get('imtID'),
    #             title=item.get('title'),
    #             vendor_code=item.get('vendorCode'),
    #             seller_id=seller.id,
    #             seller=seller
    #         )
    #         cards_to_insert.append(card)

    # # Bulk save for efficiency
    # if cards_to_insert:
    #     session.bulk_save_objects(cards_to_insert)

    # if cards_to_update:
    #     session.bulk_save_objects(cards_to_update)

    # # Commit once for all operations
    # session.commit()
    # return cards_to_insert + cards_to_update