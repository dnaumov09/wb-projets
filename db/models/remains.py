from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship


from db.base import Base, session
from db.models.card import Card, get_seller_cards
from db.models.seller import Seller


class Remains(Base):
    __tablename__ = 'remains'

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False)
    card: Mapped[Card] = relationship("Card")

    brand: Mapped[str] = mapped_column(nullable=False)
    subject_name: Mapped[str] = mapped_column(nullable=False)
    vendor_code: Mapped[str] = mapped_column(nullable=False)
    barcode: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    tech_size: Mapped[str] = mapped_column(nullable=False)
    volume: Mapped[float] = mapped_column(nullable=False)
    in_way_to_client: Mapped[int] = mapped_column(nullable=False)
    in_way_from_client: Mapped[int] = mapped_column(nullable=False)
    quantity_warehouses_full: Mapped[int] = mapped_column(nullable=False)


def save_remains(data, seller: Seller) -> list[Remains]:
    # Fetch existing orders (barcode) in bulk
    existing_remains_list = session.scalars(select(Remains).filter(
        Remains.barcode.in_([item.get("barcode") for item in data])
    )).all()
    existing_remains = {remains.barcode: remains for remains in existing_remains_list}

    incoming_remains_barcodes = {item.get('barcode') for item in data}
    existing_remains_barcodes = set(existing_remains.keys())
    remains_to_delete = list(existing_remains_barcodes - incoming_remains_barcodes)

    card_map = {c.nm_id: c for c in get_seller_cards(seller.id)}

    new_remains = []
    existing_remains_output = []
    for item in data:
        remains_key = item.get("barcode")
        if not remains_key: #коробка barcode None
            continue

        if item.get('nmId') not in card_map:
            continue

        remains_fields = {
            "nm_id": item.get('nmId'),
            "brand": item.get('brand'), 
            "subject_name": item.get('subjectName'), 
            "vendor_code": item.get('vendorCode'),
            "barcode": item.get('barcode'),
            "tech_size": item.get('techSize'),
            "volume": item.get('volume'),
            "in_way_to_client": item.get('inWayToClient'),
            "in_way_from_client": item.get('inWayFromClient'),
            "quantity_warehouses_full": item.get('quantityWarehousesFull')
        }

        if remains_key in existing_remains:
            # Update existing advert
            remians = existing_remains[remains_key]
            for field, value in remains_fields.items():
                setattr(remians, field, value)
            existing_remains_output.append(remians)
        else:
            # Collect for bulk insert
            new_remains.append(Remains(**remains_fields))


    if new_remains:
        session.bulk_save_objects(new_remains)

    if remains_to_delete:
        for remains in remains_to_delete:
            session.delete(remains)

    session.commit()
    return new_remains + existing_remains_output



# def save_or_update_remains(card: Card, data) -> Remains:
#     barcode = data.get('barcode')
#     remains = session.query(Remains).filter(Remains.nm_id == card.nm_id, Remains.barcode == barcode).first()
#     if remains:
#         remains.brand = data.get('brand')
#         remains.subject_name = data.get('subjectName')
#         remains.vendor_code = data.get('vendorCode')
#         remains.barcode = barcode
#         remains.tech_size = data.get('techSize')
#         remains.volume = data.get('volume')
#         remains.in_way_to_client = data.get('inWayToClient')
#         remains.in_way_from_client = data.get('inWayFromClient')
#         remains.quantity_warehouses_full = data.get('quantityWarehousesFull')
#     else:
#         remains = Remains(
#             nm_id=card.nm_id,
#             card=card, 
#             brand=data.get('brand'), 
#             subject_name=data.get('subjectName'), 
#             vendor_code=data.get('vendorCode'),
#             barcode=data.get('barcode'),
#             tech_size=data.get('techSize'),
#             volume=data.get('volume'),
#             in_way_to_client=data.get('inWayToClient'),
#             in_way_from_client=data.get('inWayFromClient'),
#             quantity_warehouses_full=data.get('quantityWarehousesFull')
#         )
#         session.add(remains)
#     session.commit()
#     return remains

def get_remains_by_seller_id(seller_id: int) -> list[Remains]:
    return (
        session.query(Remains)
        .join(Remains.card).join(Card.seller)
        .filter(Card.seller_id == seller_id)
        .all()
    )


def get_remains_by_seller_id(seller_id: int):
    return (
        session.query(Remains)
            .join(Card, Card.nm_id == Remains.nm_id)
            .join(Seller, Seller.id == Card.seller_id)
            .filter(Seller.id == seller_id).all()
    )