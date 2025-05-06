from enum import Enum
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Index, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.model.card import Card
from db.util import convert_date, save_records, camel_to_snake
from db.base import Base

from admin.model import Seller
from admin.db_router import get_session


class OrderStatus(Enum):
    UNDEFINED = -1
    NEW = 0
    ACCEPTED_TO_WH = 1
    CANCELLED = 2


class Order(Base):
    __tablename__ = 'orders'

    __table_args__ = (
        Index('idx_orders_cancel_date_nmid', 'cancel_date', 'nm_id'),  # Composite index
        Index('idx_orders_date_nmid', 'date', 'nm_id'),  # Composite index
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_change_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    warehouse_name: Mapped[str] = mapped_column(nullable=False)
    warehouse_type: Mapped[str] = mapped_column(nullable=False)
    country_name: Mapped[str] = mapped_column(nullable=False)
    oblast_okrug_name: Mapped[str] = mapped_column(nullable=False)
    region_name: Mapped[str] = mapped_column(nullable=False)
    supplier_article: Mapped[str] = mapped_column(nullable=False)

    nm_id: Mapped[int] = mapped_column(ForeignKey('cards.nm_id'), nullable=False) #Артикул WB
    card: Mapped[Card] = relationship("Card")

    barcode: Mapped[str] = mapped_column(nullable=False) #Баркод
    category: Mapped[str] = mapped_column(nullable=False) #Категория
    subject: Mapped[str] = mapped_column(nullable=False) #Предмет
    brand: Mapped[str] = mapped_column(nullable=False) #Бренд
    tech_size: Mapped[str] = mapped_column(nullable=False) #Размер товара
    income_id: Mapped[str] = mapped_column(nullable=False) #Номер поставки
    is_supply: Mapped[bool] = mapped_column(nullable=False) #Договор поставки
    is_realization: Mapped[bool] = mapped_column(nullable=False) #Договор реализации
    total_price: Mapped[float] = mapped_column(nullable=False) #Цена без скидок
    discount_percent: Mapped[float] = mapped_column(nullable=False) #Скидка продавца
    spp: Mapped[float] = mapped_column(nullable=False) #Скидка WB
    finished_price: Mapped[float] = mapped_column(nullable=False) #Цена с учетом всех скидок, кроме суммы по WB Кошельку
    price_with_disc: Mapped[float] = mapped_column(nullable=False) #Цена со скидкой продавца (= totalPrice * (1 - discountPercent/100))
    is_cancel: Mapped[bool] = mapped_column(nullable=False)
    cancel_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    order_type: Mapped[str] = mapped_column(nullable=True) #Тип заказа
    sticker: Mapped[str] = mapped_column(nullable=True) #ID стикера
    g_number: Mapped[str] = mapped_column(nullable=True) #Номер заказа
    srid: Mapped[str] = mapped_column(nullable=True) #Уникальный ID заказа WB
    status: Mapped[OrderStatus] = mapped_column(PgEnum(OrderStatus, native_enum=False), nullable=True)


def define_existing_order_status(sticker: str = '', is_cancel: bool = False):
    if sticker == '':
        status = OrderStatus.NEW
    else:
        status = OrderStatus.ACCEPTED_TO_WH
    
    if is_cancel:
        status = OrderStatus.CANCELLED
    
    return status if status else OrderStatus.UNDEFINED


def save_orders(seller: Seller, data) -> list[Order]:
    updated_data = []
    for item in data:
        item = {camel_to_snake(k): v for k, v in item.items()}

        for field in ['date', 'last_change_date', 'cancel_date']:
            if field in item and isinstance(item[field], str):
                item[field] = convert_date(item[field], '%Y-%m-%dT%H:%M:%S')

        item['status'] = define_existing_order_status(sticker=item["sticker"], is_cancel=item["is_cancel"])
        updated_data.append(item)
    
    return save_records(
        session=get_session(seller),
        model=Order,
        data=updated_data,
        key_fields=['g_number', 'srid'])
