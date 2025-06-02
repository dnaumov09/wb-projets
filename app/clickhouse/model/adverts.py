from datetime import datetime, date
from typing import Iterable, Dict, Any

from admin.model import Seller
from admin.db_router import get_client

ISO_Z_TO_UTC = "Z", "+00:00" 

def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace(*ISO_Z_TO_UTC))

def _iter_advert_rows(ads: Iterable[Dict[str, Any]]):
    for item in ads:
        yield (
            item["advertId"],
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
        (advert_id, create_time, start_time, end_time,
         change_time, name, daily_budget, search_pluse_state,
         advert_type, status, payment_type)
        VALUES
        """,
        _iter_advert_rows(ads),
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


def save_advert_stat_hourly(seller: Seller, stat: list[dict[str, Any]], date: date, hour) -> None:
    client = get_client(seller)

    today_stat = client.execute(f"SELECT * FROM adverts_stat WHERE date = '{date.isoformat()}'")

    today_stat_map = {}
    for row in today_stat:
        key = (row[0], row[1], row[2], row[10])  # advert_id, date, nm_id, app_type
        today_stat_map[key] = row[3:10]  # суммы

    insert_rows = []
    for new_row in _iter_stat_rows(stat):
        if new_row[1] != date:
            continue

        key = (new_row[0], new_row[1], new_row[2], new_row[10])
        old_sums = today_stat_map.get(key, [0, 0, 0, 0, 0, 0, 0])
        sum_old, views_old, clicks_old, atbs_old, orders_old, shks_old, sum_price_old = old_sums

        # Новые значения
        sum_new = new_row[3]
        views_new = new_row[4]
        clicks_new = new_row[5]
        atbs_new = new_row[6]
        orders_new = new_row[7]
        shks_new = new_row[8]
        sum_price_new = new_row[9]

        # Дельты
        sum_delta = max(sum_new - sum_old, 0)
        views_delta = max(views_new - views_old, 0)
        clicks_delta = max(clicks_new - clicks_old, 0)
        atbs_delta = max(atbs_new - atbs_old, 0)
        orders_delta = max(orders_new - orders_old, 0)
        shks_delta = max(shks_new - shks_old, 0)
        sum_price_delta = max(sum_price_new - sum_price_old, 0)

        insert_rows.append((
            new_row[0], new_row[1], new_row[2], sum_delta,
            views_delta, clicks_delta, atbs_delta, orders_delta, shks_delta,
            sum_price_delta, new_row[10], hour
        ))
    
    # 3️⃣ Вставляем дельты в ClickHouse
    if insert_rows:
        client.execute(
            """
            INSERT INTO adverts_stat_hourly
                (advert_id, date, nm_id, sum, views, clicks,
                atbs, orders, shks, sum_price, app_type, hour)
            VALUES
            """,
            insert_rows,
        )
