from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.model import Base, session
from db.card import Card
from db.order import Order
from datetime import datetime
from enum import Enum

class SaleStatus(Enum):
    UNDEFINED = -1
    NEW = 0

class Sale(Base):
    __tablename__ = 'sales'

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
    for_pay: Mapped[float] = mapped_column(nullable=False) #Сумма к оплате
    finished_price: Mapped[float] = mapped_column(nullable=False) #Оплачено с WB Кошелька
    price_with_disc: Mapped[float] = mapped_column(nullable=False) #К перечислению продавцу
    sale_id: Mapped[str] = mapped_column(nullable=False) #Номер продажи
    order_type: Mapped[str] = mapped_column(nullable=False) #Тип заказа
    sticker: Mapped[str] = mapped_column(nullable=True) #ID стикера
    g_number: Mapped[str] = mapped_column(nullable=True) #Номер заказа
    srid: Mapped[str] = mapped_column(nullable=True) #Уникальный ID заказа WB
    status: Mapped[SaleStatus] = mapped_column(nullable=True)


#TODO отфилльтровать по полю is_cancel и сохранять батчем 2 массива
def save(
    date, last_change_date, warehouse_name, warehouseType, country_name, oblast_okrug_name, 
    region_name, supplier_article, card, barcode, category, subject, brand, tech_size, 
    income_id, is_supply, is_realization, total_price, discount_percent, spp, for_pay,
    finished_price, price_with_disc, sale_id, order_type, sticker, g_number, srid
):
    # Check if an order with the same g_number and srid exists
    obj = session.query(Sale).filter_by(g_number=g_number, srid=srid).first()

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
        obj.for_pay = for_pay
        obj.finished_price = finished_price
        obj.price_with_disc = price_with_disc
        obj.sale_id = sale_id
        obj.order_type = order_type
        obj.sticker = sticker
    else:
        # Create new sale
        obj = Sale(
            date=date, last_change_date=last_change_date, warehouse_name=warehouse_name, warehouseType=warehouseType,
            country_name=country_name, oblast_okrug_name=oblast_okrug_name, region_name=region_name, supplier_article=supplier_article,
            card=card, barcode=barcode, category=category, subject=subject, brand=brand, tech_size=tech_size,
            income_id=income_id, is_supply=is_supply, is_realization=is_realization, total_price=total_price,
            discount_percent=discount_percent, spp=spp, for_pay=for_pay, finished_price=finished_price, 
            price_with_disc=price_with_disc, sale_id=sale_id, order_type=order_type, sticker=sticker,
            g_number=g_number, srid=srid
        )
        session.add(obj)
    
    obj.status = define_existing_sale_status(obj)
    session.commit()
    return obj


def define_existing_sale_status(obj: Order):
    if not obj.status:
        status = SaleStatus.NEW
    
    return status if status else SaleStatus.UNDEFINED