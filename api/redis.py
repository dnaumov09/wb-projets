import os
import json
import redis

from datetime import datetime

REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_USERNAME=os.getenv('REDIS_USERNAME')
REDIS_PASSWORD=os.getenv('REDIS_PASSWORD')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)
r.flushall()

LATS_UPDATED_DATA_FORMAT = '%Y-%m-%d %H:%M:%S'

KEY_TEMPLATE_KEYWORDS_STAT = "keywords_stat:advert:{advert_id}:date:{date}:keyword:{keyword}"
KEY_TEMPLATE_EXCLUDED = "keywords_excluded:advert_id:{advert_id}:excluded:{excluded}"
KEY_TEMPLATE_CLUSTER = "keywords_cluster:advert_id:{advert_id}:cluster:{cluster}"
KEY_TEMPLATE_KEYWORD = "keywords_keyword:advert_id:{advert_id}:cluster:{cluster}:keyword:{keyword}"


def sync_redis_keys(
    items,
    key_generator_fn,
    mapping_fn,
    existing_key_pattern = None
):
    # Start pipeline
    pipeline = r.pipeline()

    now_str = datetime.now().strftime(LATS_UPDATED_DATA_FORMAT)
    
    if existing_key_pattern:
        # Generate set of new keys
        new_keys = {key_generator_fn(item) for item in items}
        # Fetch existing keys
        existing_keys = {key.decode() for key in r.keys(existing_key_pattern)}
        keys_to_delete = list(existing_keys - new_keys)
        if keys_to_delete:
            pipeline.delete(*keys_to_delete)

    # Write new values
    for item in items:
        key = key_generator_fn(item)
        mapping = mapping_fn(item, now_str)
        pipeline.hset(key, mapping=mapping)

    pipeline.execute()


def save_clusters(cluster):
    def cluster_key(item):
        return KEY_TEMPLATE_CLUSTER.format(advert_id=item['advert_id'], cluster=item['name'])

    def cluster_mapping(item, now_str):
        return {
            'last_updated': now_str,
            'count': item['count']
        }

    sync_redis_keys(
        items=cluster,
        key_generator_fn=cluster_key,
        mapping_fn=cluster_mapping,
        existing_key_pattern=KEY_TEMPLATE_CLUSTER.format(advert_id='*', cluster='*')
    )


def save_keywords(cluster):
    # Flatten cluster to (advert_id, cluster_name, keyword) items
    keyword_items = [
        {'advert_id': item['advert_id'], 'cluster': item['name'], 'keyword': keyword}
        for item in cluster
        for keyword in item['keywords']
    ]

    def keyword_key(item):
        return KEY_TEMPLATE_KEYWORD.format(
            advert_id=item['advert_id'], cluster=item['cluster'], keyword=item['keyword']
        )

    def keyword_mapping(item, now_str):
        return {'last_updated': now_str}

    sync_redis_keys(
        items=keyword_items,
        key_generator_fn=keyword_key,
        mapping_fn=keyword_mapping,
        existing_key_pattern=KEY_TEMPLATE_KEYWORD.format(advert_id='*', cluster='*', keyword='*')
    )


def save_excluded(excluded):
    # Flatten excluded to (advert_id, keyword) items
    keyword_items = [
        {'advert_id': item['advert_id'], 'keyword': keyword}
        for item in excluded
        for keyword in item['keywords']
    ]

    def keyword_key(item):
        return KEY_TEMPLATE_EXCLUDED.format(
            advert_id=item['advert_id'], excluded=item['keyword']
        )

    def keyword_mapping(item, now_str):
        return {'last_updated': now_str}

    sync_redis_keys(
        items=keyword_items,
        key_generator_fn=keyword_key,
        mapping_fn=keyword_mapping,
        existing_key_pattern=KEY_TEMPLATE_EXCLUDED.format(advert_id='*', excluded='*')
    )


def save_advert_keywords(clusters, excluded):
    save_clusters(clusters)
    save_keywords(clusters)
    save_excluded(excluded)


def save_keywords_stat(data):
    stat_items = [
        {
            'advert_id': item['advert_id'], 
            'date': stat_entry['date'], 
            'keyword': stat['keyword'],
            'clicks': stat['clicks'],
            'ctr': stat['ctr'],
            'sum': stat['sum'],
            'views': stat['views']
            }
        for item in data
        for stat_entry in item['stat']
        for stat in stat_entry['stats']
    ]

    def keyword_key(item):
        return KEY_TEMPLATE_KEYWORDS_STAT.format(
            advert_id=item['advert_id'], date=item['date'], keyword=item['keyword']
        )

    def keyword_mapping(item, now_str):
        return {
            'clicks': item['clicks'],
            'ctr': item['ctr'],
            'sum': item['sum'],
            'views': item['views']
            }
    
    sync_redis_keys(
        items=stat_items,
        key_generator_fn=keyword_key,
        mapping_fn=keyword_mapping
    )

    # for item in data:
    #     advert_id = item['advert_id']
    #     for stat_entry in item['stat']:
    #         date = stat_entry['date']
    #         for stat in stat_entry['stats']:
    #             pipeline.hset(
    #                 KEY_TEMPLATE_KEYWORDS_STAT.format(advert_id=advert_id, date=date, keyword=stat['keyword']),
    #                 mapping={
    #                     'clicks': stat['clicks'],
    #                     'ctr': stat['ctr'],
    #                     'sum': stat['sum'],
    #                     'views': stat['views']
    #                 })

    # pipeline.execute()