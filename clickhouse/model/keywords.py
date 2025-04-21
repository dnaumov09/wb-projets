from datetime import datetime

from clickhouse.base import client


def save_keywords_clusters(clusters):
    cluster_items = [
        (item['advert_id'], item['name'], item['count'])
        for item in clusters
    ]
    client.execute('TRUNCATE TABLE keywords_clusters')
    client.execute('INSERT INTO clusters (advert_id, name, count) VALUES', cluster_items)

    keyword_items = [
        (item['advert_id'], item['name'], keyword)
        for item in clusters
        for keyword in item['keywords']
    ]
    client.execute('TRUNCATE TABLE keywords_keywords')
    client.execute('INSERT INTO keywords (advert_id, cluster, keyword) VALUES', keyword_items)


def save_keywords_excluded(excluded):
    cluster_items = [
        (item['advert_id'], keyword)
        for item in excluded
        for keyword in item['keywords']
    ]
    client.execute('TRUNCATE TABLE keywords_excluded')
    client.execute('INSERT INTO excluded (advert_id, keyword) VALUES', cluster_items)


def save_keywords_stat(stat):
    stat_items = [
        (item['advert_id'], datetime.strptime(stat['date'], "%Y-%m-%d"), stats['keyword'], stats['views'], stats['clicks'], stats['ctr'], stats['sum'])
        for item in stat
        for stat in item['stat']
        for stats in stat['stats']
    ]        
    client.execute('INSERT INTO keywords_stat (advert_id, date, keyword, views, clicks, ctr, sum) VALUES', stat_items)