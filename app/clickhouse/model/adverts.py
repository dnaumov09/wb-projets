from datetime import datetime
from typing import Iterable, Dict, Any

from admin.model import Seller
from admin.db_router import get_client

ISO_Z_TO_UTC = "Z", "+00:00" 

def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace(*ISO_Z_TO_UTC))

def _iter_advert_rows(ads: Iterable[Dict[str, Any]], seller_id: int):
    for item in ads:
        yield (
            item["advertId"],
            seller_id,
            _parse_iso(item["createTime"]),
            _parse_iso(item["startTime"]),
            _parse_iso(item["endTime"]),
            _parse_iso(item["changeTime"]),
            item.get("name"),     
            item.get("dailyBudget"),
            item.get("searchPluseState", None),
            item.get("type"),
            item.get("status"),
            item.get("paymentType"),
        )


def save_adverts(seller: Seller, ads: list[dict[str, Any]]) -> None:
    get_client(seller).execute("TRUNCATE TABLE adverts")

    get_client(seller).execute(
        """
        INSERT INTO adverts
        (advert_id, seller_id, create_time, start_time, end_time,
         change_time, name, daily_budget, search_pluse_state,
         advert_type, status, payment_type)
        VALUES
        """,
        _iter_advert_rows(ads, seller.id),
    )


def _iter_stat_rows(ads: Iterable[Dict[str, Any]]) -> Iterable[tuple]:
    for advert in ads:
        advert_id = advert["advertId"]
        for day in advert["days"]:
            date = datetime.fromisoformat(day["date"]).date()
            for app in day["apps"]:
                app_type = app["appType"]
                for nm in app["nm"]:
                    yield (
                        advert_id,
                        date,
                        nm["nmId"],
                        nm["sum"],
                        nm["views"],
                        nm["clicks"],
                        nm["atbs"],
                        nm["orders"],
                        nm["shks"],
                        nm["sum_price"],
                        app_type,
                    )


def _collect_dates(stat: Iterable[Dict[str, Any]]) -> set[str]:
    return {
        datetime.fromisoformat(day["date"]).date().isoformat()
        for advert in stat
        for day in advert["days"]
    }


def save_advert_stat(seller: Seller, stat: list[dict[str, Any]]) -> None:
    client = get_client(seller)
    dates = _collect_dates(stat)
    
    client.execute(f"ALTER TABLE adverts_stat DELETE WHERE date IN %(dates)s", {"dates": list(dates)})

    client.execute(
        """
        INSERT INTO adverts_stat
            (advert_id, date, nm_id, sum, views, clicks,
             atbs, orders, shks, sum_price, app_type)
        VALUES
        """,
        _iter_stat_rows(stat),
    )