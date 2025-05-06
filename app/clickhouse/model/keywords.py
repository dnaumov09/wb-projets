from datetime import datetime
from typing import Iterable, Dict, Any

from db.model.seller import Seller

from admin.db_router import get_client


def save_keywords_clusters(seller: Seller, clusters):
    client = get_client(seller)
    
    cluster_items = [
        (item['advert_id'], item['name'], item['count'])
        for item in clusters
    ]
    client.execute('TRUNCATE TABLE clusters')
    client.execute('INSERT INTO clusters (advert_id, name, count) VALUES', cluster_items)

    keyword_items = [
        (item['advert_id'], item['name'], keyword)
        for item in clusters
        for keyword in item['keywords']
    ]
    client.execute('TRUNCATE TABLE keywords')
    client.execute('INSERT INTO keywords (advert_id, cluster, keyword) VALUES', keyword_items)


def save_keywords_excluded(seller: Seller, excluded):
    client = get_client(seller)

    cluster_items = [
        (item['advert_id'], keyword)
        for item in excluded
        for keyword in item['keywords']
    ]
    client.execute('TRUNCATE TABLE excluded')
    client.execute('INSERT INTO excluded (advert_id, keyword) VALUES', cluster_items)


def _iter_stat_rows(kw_stat: Iterable[Dict[str, Any]]) -> Iterable[tuple]:
    for item in kw_stat:
        advert_id = item["advert_id"]
        for stat in item['stat']:
            date = datetime.strptime(stat['date'], "%Y-%m-%d")
            for stats in stat['stats']:
                yield (
                        advert_id,
                        date,
                        stats['keyword'], 
                        stats['views'], 
                        stats['clicks'], 
                        stats['ctr'], 
                        stats['sum']
                    )


def _collect_dates(kw_stat: Iterable[Dict[str, Any]]) -> set[str]:
    return {
        datetime.strptime(stat['date'], "%Y-%m-%d").date()
        for item in kw_stat
        for stat in item['stat']
    }


def save_keywords_stat(seller: Seller, stat):
    client = get_client(seller)
    dates = _collect_dates(stat)
    
    client.execute(f"ALTER TABLE keywords_stat DELETE WHERE date IN %(dates)s", {"dates": list(dates)})
    client.execute(
        """
        INSERT INTO keywords_stat
            (advert_id, date, keyword, views, clicks, ctr, sum)
        VALUES
        """,
        _iter_stat_rows(stat),
    )