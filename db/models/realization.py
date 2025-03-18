from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, BigInteger

from db.base import Base, session

# https://dev.wildberries.ru/openapi/financial-reports-and-accounting#tag/Finansovye-otchyoty/paths/~1api~1v5~1supplier~1reportDetailByPeriod/get
class Realization(Base):
    __tablename__ = 'realizations'
    
    realizationreport_id = Column(Integer)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    create_dt = Column(DateTime)
    fix_tariff_date_from = Column(DateTime)
    fix_tariff_date_to = Column(DateTime)
    order_dt = Column(DateTime)
    sale_dt = Column(DateTime)
    rr_dt = Column(DateTime)
    
    currency_name = Column(String)
    suppliercontract_code = Column(String, nullable=True)
    rrd_id = Column(BigInteger, primary_key=True, autoincrement=False)
    gi_id = Column(Integer)
    dlv_prc = Column(Float)
    subject_name = Column(String)
    nm_id = Column(Integer)
    brand_name = Column(String)
    sa_name = Column(String)
    ts_name = Column(String)
    barcode = Column(String)
    doc_type_name = Column(String)
    quantity = Column(Integer)
    retail_price = Column(Float)
    retail_amount = Column(Float)
    sale_percent = Column(Float)
    commission_percent = Column(Float)
    office_name = Column(String)
    supplier_oper_name = Column(String)
    shk_id = Column(BigInteger)
    retail_price_withdisc_rub = Column(Float)
    delivery_amount = Column(Float)
    return_amount = Column(Float)
    delivery_rub = Column(Float)
    gi_box_type_name = Column(String)
    product_discount_for_report = Column(Float)
    supplier_promo = Column(Float)
    rid = Column(BigInteger)
    ppvz_spp_prc = Column(Float)
    ppvz_kvw_prc_base = Column(Float)
    ppvz_kvw_prc = Column(Float)
    sup_rating_prc_up = Column(Float)
    is_kgvp_v2 = Column(Integer)
    ppvz_sales_commission = Column(Float)
    ppvz_for_pay = Column(Float)
    ppvz_reward = Column(Float)
    acquiring_fee = Column(Float)
    acquiring_percent = Column(Float)
    payment_processing = Column(String)
    acquiring_bank = Column(String)
    ppvz_vw = Column(Float)
    ppvz_vw_nds = Column(Float)
    ppvz_office_name = Column(String)
    ppvz_office_id = Column(Integer)
    ppvz_supplier_id = Column(Integer)
    ppvz_supplier_name = Column(String)
    ppvz_inn = Column(String)
    declaration_number = Column(String)
    bonus_type_name = Column(String)
    sticker_id = Column(String)
    site_country = Column(String)
    srv_dbs = Column(Boolean)
    penalty = Column(Float)
    additional_payment = Column(Float)
    rebill_logistic_cost = Column(Float)
    rebill_logistic_org = Column(String)
    storage_fee = Column(Float)
    deduction = Column(Float)
    acceptance = Column(Float)
    assembly_id = Column(Integer)
    kiz = Column(Text)
    srid = Column(String)
    report_type = Column(Integer)
    is_legal_entity = Column(Boolean)
    trbx_id = Column(String)


def save_realizations(data):
    date_keys = ['date_from', 'date_to', 'create_dt', 'fix_tariff_date_from', 'fix_tariff_date_to', 'order_dt', 'sale_dt', 'rr_dt']
    for item in data:
        for key in date_keys:
            if item[key]:
                fmt = "%Y-%m-%dT%H:%M:%SZ" if "T" in item[key] else "%Y-%m-%d"
                item[key] = datetime.strptime(item[key], fmt)
            else:
                item[key] = None

    reports_to_save = []
    for item in data:
        reports_to_save.append(Realization(**item))
    
    if reports_to_save:
        session.bulk_save_objects(reports_to_save)
    session.commit()
