from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.model import Base, session
from db.card import Card
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    UNDEFINED = -1
    NEW = 0
    ACCEPTED_TO_WH = 1
    CANCELLED = 2


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_change_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    warehouse_name: Mapped[str] = mapped_column(nullable=False)
    warehouseType: Mapped[str] = mapped_column(nullable=False)
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
    order_type: Mapped[str] = mapped_column(nullable=False) #Тип заказа
    sticker: Mapped[str] = mapped_column(nullable=True) #ID стикера
    g_number: Mapped[str] = mapped_column(nullable=True) #Номер заказа
    srid: Mapped[str] = mapped_column(nullable=True) #Уникальный ID заказа WB
    status: Mapped[OrderStatus] = mapped_column(nullable=True)


#TODO отфилльтровать по полю is_cancel и сохранять батчем 2 массива
def save(
    date, last_change_date, warehouse_name, warehouseType, country_name, oblast_okrug_name, 
    region_name, supplier_article, card, barcode, category, subject, brand, tech_size, 
    income_id, is_supply, is_realization, total_price, discount_percent, spp, finished_price, 
    price_with_disc, is_cancel, cancel_date, order_type, sticker, g_number, srid
):
    # Check if an order with the same g_number and srid exists
    obj = session.query(Order).filter_by(g_number=g_number, srid=srid).first()

    if obj:
        # Update existing order
        obj.date = date
        obj.last_change_date = last_change_date
        obj.warehouse_name = warehouse_name
        obj.warehouseType = warehouseType
        obj.country_name = country_name
        obj.oblast_okrug_name = oblast_okrug_name
        obj.region_name = region_name
        obj.supplier_article = supplier_article
        obj.card = card
        obj.barcode = barcode
        obj.category = category
        obj.subject = subject
        obj.brand = brand
        obj.tech_size = tech_size
        obj.income_id = income_id
        obj.is_supply = is_supply
        obj.is_realization = is_realization
        obj.total_price = total_price
        obj.discount_percent = discount_percent
        obj.spp = spp
        obj.finished_price = finished_price
        obj.price_with_disc = price_with_disc
        obj.is_cancel = is_cancel
        obj.cancel_date = cancel_date
        obj.order_type = order_type
        obj.sticker = sticker
    else:
        # Create new order
        obj = Order(
            date=date, last_change_date=last_change_date, warehouse_name=warehouse_name, warehouseType=warehouseType,
            country_name=country_name, oblast_okrug_name=oblast_okrug_name, region_name=region_name, supplier_article=supplier_article,
            card=card, barcode=barcode, category=category, subject=subject, brand=brand, tech_size=tech_size,
            income_id=income_id, is_supply=is_supply, is_realization=is_realization, total_price=total_price,
            discount_percent=discount_percent, spp=spp, finished_price=finished_price, price_with_disc=price_with_disc,
            is_cancel=is_cancel, cancel_date=cancel_date, order_type=order_type, sticker=sticker,
            g_number=g_number, srid=srid
        )
        session.add(obj)
    
    obj.status = define_existing_order_status(obj)
    session.commit()
    return obj


def define_existing_order_status(obj: Order):
    if not obj.status:
        status = OrderStatus.NEW

    if obj.sticker != '':
        status = OrderStatus.ACCEPTED_TO_WH
    
    if obj.is_cancel:
        status = OrderStatus.CANCELLED
    
    return status if status else OrderStatus.UNDEFINED