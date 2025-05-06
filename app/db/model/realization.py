from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean, DateTime, Text, BigInteger
from sqlalchemy.orm import relationship

from db.base import Base
from db.util import convert_date, save_records, camel_to_snake

from admin.model import Seller
from admin.db_router import get_session

# https://dev.wildberries.ru/openapi/financial-reports-and-accounting#tag/Finansovye-otchyoty/paths/~1api~1v5~1supplier~1reportDetailByPeriod/get
class Realization(Base):
    __tablename__ = 'realizations'
    
    realizationreport_id = Column(Integer)                                  # Номер отчёта
    date_from = Column(DateTime)                                            # Дата начала отчётного периода
    date_to = Column(DateTime)                                              # Дата конца отчётного периода
    create_dt = Column(DateTime)                                            # Дата формирования отчёта
    currency_name = Column(String)                                          # Валюта отчёта
    suppliercontract_code = Column(String, nullable=True)                   # Договор
    rrd_id = Column(BigInteger, primary_key=True, autoincrement=False)      # Номер строки
    gi_id = Column(Integer)                                                 # Номер поставки
    dlv_prc = Column(Float)                                                 # Фиксированный коэффициент склада по поставке
    fix_tariff_date_from = Column(DateTime)                                 # Дата начала действия фиксации
    fix_tariff_date_to = Column(DateTime)                                   # Дата окончания действия фиксации
    subject_name = Column(String)                                           # Предмет
    nm_id = Column(Integer)                                                 # Артикул WB
    brand_name = Column(String)                                             # Бренд
    sa_name = Column(String)                                                # Артикул продавца
    ts_name = Column(String)                                                # Размер
    barcode = Column(String)                                                # Баркод
    doc_type_name = Column(String)                                          # Тип документа
    quantity = Column(Integer)                                              # Количество
    retail_price = Column(Float)                                            # Цена розничная
    retail_amount = Column(Float)                                           # Вайлдберриз реализовал Товар (Пр)
    sale_percent = Column(Float)                                            # Согласованная скидка, %
    commission_percent = Column(Float)                                      # Размер кВВ, %
    office_name = Column(String)                                            # Склад
    supplier_oper_name = Column(String)                                     # Обоснование для оплаты
    order_dt = Column(DateTime)                                             # Дата заказа. Присылается с явным указанием часового пояса
    sale_dt = Column(DateTime)                                              # Дата продажи. Присылается с явным указанием часового пояса
    rr_dt = Column(DateTime)                                                # Дата операции. Присылается с явным указанием часового пояса
    shk_id = Column(BigInteger)                                             # Штрихкод
    retail_price_withdisc_rub = Column(Float)                               # Цена розничная с учетом согласованной скидки
    delivery_amount = Column(Float)                                         # Количество доставок
    return_amount = Column(Float)                                           # Количество возврата
    delivery_rub = Column(Float)                                            # Услуги по доставке товара покупателю
    gi_box_type_name = Column(String)                                       # Тип коробов
    product_discount_for_report = Column(Float)                             # Согласованный продуктовый дисконт, %
    supplier_promo = Column(Float)                                          # Промокод
    rid = Column(BigInteger)                                                # Уникальный ID заказа
    ppvz_spp_prc = Column(Float)                                            # Скидка WB, %
    ppvz_kvw_prc_base = Column(Float)                                       # Размер кВВ без НДС, % базовый
    ppvz_kvw_prc = Column(Float)                                            # Итоговый кВВ без НДС, %
    sup_rating_prc_up = Column(Float)                                       # Размер снижения кВВ из-за рейтинга, %
    is_kgvp_v2 = Column(Integer)                                            # Размер снижения кВВ из-за акции, %
    ppvz_sales_commission = Column(Float)                                   # Вознаграждение с продаж до вычета услуг поверенного, без НДС
    ppvz_for_pay = Column(Float)                                            # К перечислению продавцу за реализованный товар
    ppvz_reward = Column(Float)                                             # Возмещение за выдачу и возврат товаров на ПВЗ
    acquiring_fee = Column(Float)                                           # Эквайринг/Комиссии за организацию платежей
    acquiring_percent = Column(Float)                                       # Размер комиссии за эквайринг/Комиссии за организацию платежей, %
    payment_processing = Column(String)                                     # Тип платежа за Эквайринг/Комиссии за организацию платежей
    acquiring_bank = Column(String)                                         # Наименование банка-эквайера
    ppvz_vw = Column(Float)                                                 # Вознаграждение Вайлдберриз (ВВ), без НДС
    ppvz_vw_nds = Column(Float)                                             # НДС с вознаграждения WB
    ppvz_office_name = Column(String)                                       # Наименование офиса доставки
    ppvz_office_id = Column(Integer)                                        # Номер офиса
    ppvz_supplier_id = Column(Integer)                                      # Номер партнёра
    ppvz_supplier_name = Column(String)                                     # Наименование партнёра
    ppvz_inn = Column(String)                                               # ИНН партнёра
    declaration_number = Column(String)                                     # Номер таможенной декларации
    bonus_type_name = Column(String)                                        # Виды логистики, штрафов и доплат. Поле будет в ответе при наличии значения
    sticker_id = Column(String)                                             # Цифровое значение стикера, который клеится на товар в процессе сборки заказа по схеме "Маркетплейс"
    site_country = Column(String)                                           # Страна продажи
    srv_dbs = Column(Boolean)                                               # Признак услуги платной доставки
    penalty = Column(Float)                                                 # Общая сумма штрафов
    additional_payment = Column(Float)                                      # Доплаты
    rebill_logistic_cost = Column(Float)                                    # Возмещение издержек по перевозке/по складским операциям с товаром
    rebill_logistic_org = Column(String)                                    # Организатор перевозки. Поле будет в ответе при наличии значения
    storage_fee = Column(Float)                                             # Стоимость хранения
    deduction = Column(Float)                                               # Прочие удержания/выплаты
    acceptance = Column(Float)                                              # Стоимость платной приёмки
    assembly_id = Column(Integer)                                           # Номер сборочного задания
    kiz = Column(Text)                                                      # Код маркировки. Поле будет в ответе при наличии значения
    srid = Column(String)                                                   # Уникальный ID заказа. Примечание для использующих API Marketplace: srid равен rid в ответах методов сборочных заданий.
    report_type = Column(Integer)                                           # Тип отчёта: 1 — стандартный, 2 — для уведомления о выкупе
    is_legal_entity = Column(Boolean)                                       # Признак B2B-продажи
    trbx_id = Column(String)                                                # Номер короба для платной приёмки


def save_realizations(data, seller: Seller):
    data = [
        {camel_to_snake(k): v for k, v in item.items()}
        for item in data
    ]
    
    date_keys = [
        'date_from', 'date_to', 'create_dt', 'fix_tariff_date_from', 
        'fix_tariff_date_to', 'order_dt', 'sale_dt', 'rr_dt'
    ]
    
    for item in data:
        for key in date_keys:
            if key in item and item[key]:
                fmt = "%Y-%m-%dT%H:%M:%SZ" if "T" in item[key] else "%Y-%m-%d"
                item[key] = convert_date(item[key], fmt)
            else:
                item[key] = None

    return save_records(
        session=get_session(seller),
        model=Realization,
        data=data,
        key_fields=['rrd_id'])
