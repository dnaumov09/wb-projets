from datetime import datetime, date
from typing import Iterable, Dict, Any

from admin.model import Seller
from admin.db_router import get_client


def _collect_dates(stat: Iterable[Dict[str, Any]]) -> set[str]:
    return {
        datetime.fromisoformat(day["dt"]).date().isoformat()
        for advert in stat
        for day in advert["history"]
    }


def _iter_stat_rows(stat: Iterable[Dict[str, Any]]) -> Iterable[tuple]:
    for card in stat:
        nm_id = card["nmID"]
        for day in card["history"]:
            date = datetime.fromisoformat(day["dt"]).date()
            yield (
                nm_id,
                date,
                day["openCardCount"],
                day["addToCartCount"],
                day["ordersCount"],
                day["ordersSumRub"],
                day["buyoutsCount"],
                day["buyoutsSumRub"]
            )


def save_cards_stat(seller: Seller, stat: list[dict[str, Any]]):
    client = get_client(seller)
    dates = _collect_dates(stat)
    
    client.execute(f"ALTER TABLE cards_stat DELETE WHERE date IN %(dates)s", {"dates": list(dates)})

    client.execute(
        """
        INSERT INTO cards_stat
            (nm_id, date, open_card_count, add_to_cart_count, orders_count, orders_sum_rub,
             buyouts_count, buyouts_sum_rub)
        VALUES
        """,
        _iter_stat_rows(stat),
    )


def save_cards_stat_hourly(seller: Seller, stat: list[dict[str, Any]], date: date, hour) -> None:
    client = get_client(seller)

    today_stat = client.execute(f"SELECT * FROM cards_stat WHERE date = '{date.isoformat()}'")

    today_stat_map = {}
    for row in today_stat:
        key = (row[0], row[1])  # nm_id, date
        today_stat_map[key] = row[2:]  # суммы

    insert_rows = []
    for new_row in _iter_stat_rows(stat):
        if new_row[1] != date:
            continue

        key = (new_row[0], new_row[1])
        old_sums = today_stat_map.get(key, [0, 0, 0, 0, 0, 0])
        open_card_old, add_to_cart_old, orders_old, oreders_sum_old, buyouts_old, buyouts_sum_old = old_sums

        # Новые значения
        open_card_new = new_row[2]
        add_to_cart_new = new_row[3]
        orders_new = new_row[4]
        orders_sum_new = new_row[5]
        buyouts_new = new_row[6]
        buyouts_sum_new = new_row[7]

        # Дельты
        open_card_delta = max(open_card_new - open_card_old, 0)
        add_to_cart_delta = max(add_to_cart_new - add_to_cart_old, 0)
        orders_delta = max(orders_new - orders_old, 0)
        orders_sum_delta = max(orders_sum_new - oreders_sum_old, 0)
        buyouts_delta = max(buyouts_new - buyouts_old, 0)
        buyouts_sum_delta = max(buyouts_sum_new - buyouts_sum_old, 0)

        insert_rows.append((
            new_row[0], new_row[1], hour,
            open_card_delta, add_to_cart_delta, orders_delta,
            orders_sum_delta, buyouts_delta, buyouts_sum_delta
        ))

        if insert_rows:
            client.execute(
                """
                INSERT INTO cards_stat_hourly
                    (nm_id, date, hour, 
                    open_card_count, add_to_cart_count, orders_count, 
                    orders_sum_rub, buyouts_count, buyouts_sum_rub)
                VALUES
                """,
                insert_rows,
            )
