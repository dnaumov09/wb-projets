import os
import json
import redis

from datetime import datetime

REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_USERNAME=os.getenv('REDIS_USERNAME')
REDIS_PASSWORD=os.getenv('REDIS_PASSWORD')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD)
# r.flushall()

LATS_UPDATED_DATA_FORMAT = '%Y-%m-%d %H:%M:%S'

def save_cluster(cluster):
    now_str = datetime.now().strftime(LATS_UPDATED_DATA_FORMAT)

    new_keys = {
        f"keywords:advert_id:{item['advert_id']}:cluster:{item['name']}"
        for item in cluster
    }

    existing_keys = r.keys("keywords:advert_id:*:cluster:*")
    keys_to_delete = [key for key in existing_keys if key.decode('utf-8') not in new_keys]

    pipeline = r.pipeline()

    if keys_to_delete:
        pipeline.delete(*keys_to_delete)

    for item in cluster:
        key = f"keywords:advert_id:{item['advert_id']}:cluster:{item['name']}"
        mapping = {
            'last_updated': now_str,
            'count': item['count'],
            'keywords': json.dumps(item['keywords'])
        }
        pipeline.hset(key, mapping=mapping)

    pipeline.execute()


def save_excluded(excluded):
    now_str = datetime.now().strftime(LATS_UPDATED_DATA_FORMAT)

    new_keys = {
        f"keywords:advert_id:{item['advert_id']}:excluded"
        for item in excluded
    }
    
    existing_keys = r.keys("keywords:advert_id:*:excluded")
    keys_to_delete = [key for key in existing_keys if key.decode('utf-8') not in new_keys]

    pipeline = r.pipeline()

    if keys_to_delete:
        pipeline.delete(*keys_to_delete)

    for item in excluded:
        key = f"keywords:advert_id:{item['advert_id']}:excluded"
        mapping = {
            'last_updated': now_str,
            'excluded': json.dumps(item['keywords'])
        }
        pipeline.hset(key, mapping=mapping)

    pipeline.execute()


def get_cluster(advert_id: int, cluster: str):
    cluster = r.hgetall(f"keywords:advert_id:{advert_id}:cluster:{cluster}")
    decoded_data = {key.decode(): value.decode() for key, value in cluster.items()}
    decoded_data['keywords'] = json.loads(decoded_data['keywords'])
    decoded_data['count'] = int(decoded_data['count'])
    decoded_data['last_updated'] = datetime.strptime(decoded_data['last_updated'], LATS_UPDATED_DATA_FORMAT)
    return decoded_data


def get_excluded(advert_id: int):
    excluded = r.hgetall(f"keywords:advert_id:{advert_id}:excluded")
    decoded_data = {key.decode(): value.decode() for key, value in excluded.items()}
    decoded_data['excluded'] = json.loads(decoded_data['excluded'])
    decoded_data['last_updated'] = datetime.strptime(decoded_data['last_updated'], LATS_UPDATED_DATA_FORMAT)
    return decoded_data
