import logging
import os
import requests
from enum import Enum

from admin.util import generate_strong_password

TIMEWEB_TOKEN = os.getenv("TIMEWEB_TOKEN")
TIMEWEB_POSTGRES_CLUSTER_ID = os.getenv('TIMEWEB_POSTGRES_CLUSTER_ID')
TIMEWEB_CLICKHOUSE_CLUSTER_ID = os.getenv('TIMEWEB_CLICKHOUSE_CLUSTER_ID')

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + TIMEWEB_TOKEN,
}

class Cluster(Enum):
    POSTGRES = {
        'id': TIMEWEB_POSTGRES_CLUSTER_ID,
        'privileges': [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'TRUNCATE',
            'CREATE', 'TRIGGER', "REFERENCES", 
            'TEMPORARY'
        ]
        }
    CLICKHOUSE = {
        'id': TIMEWEB_CLICKHOUSE_CLUSTER_ID,
        'privileges': [
            'SELECT', 'INSERT', 'TRUNCATE', 'SHOW',
            'ALTER_TABLE', 'CREATE_TABLE', 'CREATE_VIEW', 'CREATE_DICTIONARY', 'DROP_TABLE',
            'OPTIMIZE', 'dictGet'
        ]
        }


def _get_cluster(cluster: Cluster):
    logging.info(f'--- Getting cluster')
    url = f'https://api.timeweb.cloud/api/v1/databases/{cluster.value['id']}'
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if cluster == Cluster.POSTGRES:
            port = data['db']['port']
        elif cluster == Cluster.CLICKHOUSE:
            port = 9000
        else:
            port = None
        return {
            'cluster_id': cluster.value['id'],
            'host': data['db']['networks'][1]['ips'][0]['ip'],
            'port': port
        }
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e.response.json())
    except requests.RequestException as e:
        logging.error("HTTP error: %s", e.response.json())


def _create_instance(cluster: Cluster, name: str, description: str):
    logging.info(f'--- Creating {cluster.name.lower()} instance')
    url = f"https://api.timeweb.cloud/api/v1/databases/{cluster.value['id']}/instances"
    payload = {
        'name': name,
        'description': description,
    }
    try:
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            'instance_id': data['instance']['id'],
            'name': name
        }
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e.response.json())
    except requests.RequestException as e:
        logging.error("HTTP error: %s", e.response.json())


def _delete_instance(cluster: Cluster, instance_id: int):
    url = f"https://api.timeweb.cloud/api/v1/databases/{cluster.value['id']}/instances/{instance_id}"
    try:
        response = requests.delete(url=url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e.response.json())
    except requests.RequestException as e:
        logging.error("HTTP error: %s", e.response.json())


def _create_user(cluster: Cluster, instance_id: int, username: str, description: str):
    logging.info(f'--- Creating user for {cluster.name.lower()} instance')
    url = f'https://api.timeweb.cloud/api/v1/databases/{cluster.value['id']}/admins'
    password = generate_strong_password()
    payload = {
            'login': username,
            'password': password,
            'host': '%',
            'instance_id': instance_id,
            'description': description,
            'privileges': cluster.value['privileges']
        }
    try: 
        response = requests.post(url=url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return {
            'user_id': data['admin']['id'],
            'username': username,
            'password': password
        }
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e.response.json())
    except requests.RequestException as e:
        logging.error("HTTP error: %s", e.response.json())


def _delete_user(cluster: Cluster, user_id: int):
    url = f"https://api.timeweb.cloud/api/v1/databases/{cluster.value['id']}/admins/{user_id}"
    try:
        response = requests.delete(url=url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as e:
        logging.error("HTTP error: %s", e.response.json())
    except requests.RequestException as e:
        logging.error("HTTP error: %s", e.response.json())


def create_databases(seller_info: dict):
    logging.info('💨 Creating databases...')
    instance_name = 'db_' + seller_info['sid'].replace('-', '_')
    user_name = 'user_' + seller_info['sid'].replace('-', '_')
    description = seller_info['tradeMark']

    clusters = []
    for cluster_type in Cluster:
        cluster = _get_cluster(cluster_type)
        instance = _create_instance(cluster_type, instance_name, description)

        if not instance:
            return []
        
        user = _create_user(cluster_type, instance['instance_id'], user_name, description)

        if not user:
            if instance:
                _delete_instance(cluster_type, instance['instance_id'])
            return []
        clusters.append({
            'cluster_type': cluster_type,
            'cluster': cluster,
            'instance': instance,
            'user': user,
            'description': description
        })

    logging.info('✅ Databases created')
    return clusters
        