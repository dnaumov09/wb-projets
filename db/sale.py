from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.model import Base, session
from db.card import Card
from db.order import Order
from datetime import datetime
from enum import Enum
from db.settings import set_sales_last_updated

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


def save_update_sales(data, card_map: dict[int, Card]) -> list[Sale]:
    new_last_updated = datetime.now()
    sales_to_insert = []
    sales_to_update = []

    # Fetch existing orders (g_number, srid) in bulk
    existing_sales = {
        (sale.g_number, sale.srid): sale
        for sale in session.query(Sale).filter(
            Sale.g_number.in_([item.get("gNumber") for item in data]),
            Sale.srid.in_([item.get("srid") for item in data])
        ).all()
    }

    for item in data:
        card = card_map.get(item.get("nmId"))
        sale_key = (item.get("gNumber"), item.get("srid"))

        if sale_key in existing_sales:
            # Update existing sale
            sale = existing_sales[sale_key]
            sale.date = item.get("date")
            sale.last_change_date = item.get("lastChangeDate")
            sale.warehouse_name = item.get("warehouseName")
            sale.warehouseType = item.get("warehouseType")
            sale.country_name = item.get("countryName")
            sale.oblast_okrug_name = item.get("oblastOkrugName")
            sale.region_name = item.get("regionName")
            sale.supplier_article = item.get("supplierArticle")
            sale.nm_id = card.nm_id
            sale.card = card
            sale.barcode = item.get("barcode")
            sale.category = item.get("category")
            sale.subject = item.get("subject")
            sale.brand = item.get("brand")
            sale.tech_size = item.get("techSize")
            sale.income_id = item.get("incomeID")
            sale.is_supply = item.get("isSupply")
            sale.is_realization = item.get("isRealization")
            sale.total_price = item.get("totalPrice")
            sale.discount_percent = item.get("discountPercent")
            sale.spp = item.get("spp")
            sale.for_pay = item.get("forPay")
            sale.finished_price = item.get("finishedPrice")
            sale.price_with_disc = item.get("priceWithDisc")
            sale.order_type = item.get("orderType")
            sale.sticker = item.get("sticker")
            sale.status = define_existing_sale_status(obj=sale)
            sales_to_update.append(sale)
        else:
            # Create new sale
            sale = Sale(
                date=item.get("date"),
                last_change_date=item.get("lastChangeDate"),
                warehouse_name=item.get("warehouseName"),
                warehouseType=item.get("warehouseType"),
                country_name=item.get("countryName"),
                oblast_okrug_name=item.get("oblastOkrugName"),
                region_name=item.get("regionName"),
                supplier_article=item.get("supplierArticle"),
                nm_id=card.nm_id,
                card=card,
                barcode=item.get("barcode"),
                category=item.get("category"),
                subject=item.get("subject"),
                brand=item.get("brand"),
                tech_size=item.get("techSize"),
                income_id=item.get("incomeID"),
                is_supply=item.get("isSupply"),
                is_realization=item.get("isRealization"),
                total_price=item.get("totalPrice"),
                discount_percent=item.get("discountPercent"),
                spp=item.get("spp"),
                for_pay=item.get("forPay"),
                finished_price=item.get("finishedPrice"),
                price_with_disc=item.get("priceWithDisc"),
                order_type=item.get("orderType"),
                sticker=item.get("sticker"),
                g_number=item.get("gNumber"),
                sale_id=item.get("saleID"),
                srid=item.get("srid"),
                status=define_existing_sale_status(obj=None),
            )
            sales_to_insert.append(sale)

    # Bulk save for efficiency
    if sales_to_insert:
        session.bulk_save_objects(sales_to_insert)

    if sales_to_update:
        session.bulk_save_objects(sales_to_update)

    # Commit once for all operations
    session.commit()

    set_sales_last_updated(new_last_updated)

    return sales_to_insert + sales_to_update



def define_existing_sale_status(obj: Sale = None):
    status = None

    if not obj:
        status = SaleStatus.NEW
    
    return status if status else SaleStatus.UNDEFINED