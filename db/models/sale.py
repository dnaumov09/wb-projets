from sqlalchemy import ForeignKey, DateTime, Index, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, session
from db.models.card import Card
from db.models.order import Order
from datetime import datetime
from enum import Enum
from db.models.seller import Seller


class SaleStatus(Enum):
    UNDEFINED = -1
    NEW = 0
    RETURN = 1

class Sale(Base):
    __tablename__ = 'sales'

    __table_args__ = (
        Index('idx_sales_date_nmid', 'date', 'nm_id'),  # Composite index
    )

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


def define_existing_sale_status(price_with_disc: float) -> SaleStatus:
    if price_with_disc >= 0:
        return SaleStatus.NEW
    else:
        return SaleStatus.RETURN
    

def save_sales(data, seller: Seller) -> list[Order]:
    # Fetch existing sales (g_number, srid) in bulk
    existing_sales_list = session.scalars(select(Sale).filter(
            Sale.g_number.in_([item.get("gNumber") for item in data]),
            Sale.srid.in_([item.get("srid") for item in data])
        )).all()
    existing_sales = {(sale.g_number, sale.srid): sale for sale in existing_sales_list}

    new_sales = []
    existing_sales_output = []
    for item in data:
        sale_key = (item.get("gNumber"), item.get("srid"))
        is_existing = sale_key in existing_sales
        price_with_disc = item.get("priceWithDisc")
        sale_fields = {
            "date": datetime.strptime(item.get("date"), '%Y-%m-%dT%H:%M:%S'),
            "last_change_date": datetime.strptime(item.get("lastChangeDate"), '%Y-%m-%dT%H:%M:%S'),
            "warehouse_name": item.get("warehouseName"),
            "warehouseType": item.get("warehouseType"),
            "country_name": item.get("countryName"),
            "oblast_okrug_name": item.get("oblastOkrugName"),
            "region_name": item.get("regionName"),
            "supplier_article": item.get("supplierArticle"),
            "nm_id": item.get("nmId"),
            "barcode": item.get("barcode"),
            "category": item.get("category"),
            "subject": item.get("subject"),
            "brand": item.get("brand"),
            "tech_size": item.get("techSize"),
            "income_id": item.get("incomeID"),
            "is_supply": item.get("isSupply"),
            "is_realization": item.get("isRealization"),
            "total_price": item.get("totalPrice"),
            "discount_percent": item.get("discountPercent"),
            "spp": item.get("spp"),
            "for_pay": item.get("forPay"),
            "finished_price": item.get("finishedPrice"),
            "price_with_disc": price_with_disc,
            "order_type": item.get("orderType"),
            "sticker": item.get("sticker"),
            "g_number": item.get("gNumber"),
            "sale_id": item.get("saleID"),
            "srid": item.get("srid"),
            "status": define_existing_sale_status(price_with_disc),
        }

        if is_existing:
            # Update existing advert
            sale = existing_sales[sale_key]
            for field, value in sale_fields.items():
                setattr(sale, field, value)
            existing_sales_output.append(sale)
        else:
            # Collect for bulk insert
            new_sales.append(Sale(**sale_fields))


    if new_sales:
        session.bulk_save_objects(new_sales)

    session.commit()
    return new_sales + existing_sales_output
