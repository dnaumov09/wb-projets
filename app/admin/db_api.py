import os
import logging
import psycopg2
from contextlib import contextmanager
from datetime import datetime, timedelta

from clickhouse_driver import Client
from alembic.config import Config
from alembic import command

from db.model.seller import Seller
from admin.timeweb_api import Cluster

# --- Config
ALEMBIC_CONFIG_PATH = "alembic.ini"
PG_VIEWS_SQL = './db/sql/views.sql'
PG_FUNCTIONS_SQL = './db/sql/functions.sql'
CH_SCHEMA = './clickhouse/schema.sql'

# --- Environment Variables for Admin DB
HOST = os.getenv("ADMIN_DB_HOST")
PORT = os.getenv("ADMIN_DB_PORT")
DB_NAME = os.getenv("ADMIN_DB_NAME")
USERNAME = os.getenv("ADMIN_DB_USERNAME")
PASSWORD = os.getenv("ADMIN_DB_PASSWORD")


# --- Admin DB Connection
@contextmanager
def admin_connection():
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DB_NAME,
        user=USERNAME,
        password=PASSWORD
    )
    try:
        yield conn
    finally:
        conn.close()


# --- SQL Helpers
def run_sql_file_pg(file_path: str, cursor):
    with open(file_path, 'r') as f:
        cursor.execute(f.read())


def run_sql_file_ch(file_path: str, host: str, port: str, dbname: str, username: str, password: str):
    client = Client(host=host, port=port, user=username, password=password, database=dbname)
    with open(file_path, 'r', encoding='utf-8') as f:
        for query in [q.strip() for q in f.read().split(';') if q.strip()]:
            client.execute(query)


def create_insert_query(table: str, columns: tuple, values: tuple):
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    return f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders});", values


# --- Schema Creation
def create_schema(databases: list[dict]):
    for db in databases:
        cluster_type = db['cluster_type']
        host, port = db['cluster']['host'], db['cluster']['port']
        name = db['instance']['name']
        username, password = db['user']['username'], db['user']['password']

        logging.info(f'--- Creating schema for {cluster_type.name.lower()} {host}:{port}/{name}')

        if cluster_type == Cluster.POSTGRES:
            alembic_cfg = Config(ALEMBIC_CONFIG_PATH)
            alembic_cfg.set_main_option(
                "sqlalchemy.url",
                f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{name}"
            )
            command.upgrade(alembic_cfg, "head")

            with psycopg2.connect(host=host, port=port, dbname=name, user=username, password=password) as conn:
                with conn.cursor() as cursor:
                    run_sql_file_pg(PG_VIEWS_SQL, cursor)
                    run_sql_file_pg(PG_FUNCTIONS_SQL, cursor)
        elif cluster_type == Cluster.CLICKHOUSE:
            run_sql_file_ch(CH_SCHEMA, host, port, name, username, password)


# --- Admin DB Operations
# def save_seller(seller_info: dict, databases: list[dict]):
#     logging.info('--- Saving seller to admin database')
#     with admin_connection() as conn:
#         with conn.cursor() as cur:
#             query, values = create_insert_query(
#                 'sellers',
#                 ('sid', 'name', 'trade_mark', 'token', 'active'),
#                 (seller_info['sid'], seller_info['name'], seller_info['tradeMark'], seller_info['token'], True)
#             )
#             cur.execute(query, values)

#             for db in databases:
#                 cur.execute(*create_insert_query(
#                     'seller_databases',
#                     ('host', 'port', 'name', 'seller_sid', 'database_type'),
#                     (db['cluster']['host'], db['cluster']['port'], db['instance']['name'],
#                      seller_info['sid'], db['cluster_type'].name)
#                 ))
#                 cur.execute(*create_insert_query(
#                     'database_users',
#                     ('username', 'password', 'seller_sid', 'database_type'),
#                     (db['user']['username'], db['user']['password'], seller_info['sid'], db['cluster_type'].name)
#                 ))
#         conn.commit()


# def fill_data(seller_info: dict, db: dict):
#     logging.info('--- Filling data')
#     with admin_connection() as conn:
#         with conn.cursor() as cur:
#             seller_id = 1  # TODO: remove hardcoded ID
#             cur.execute("""
#                 INSERT INTO seller (id, sid, name, trade_mark, token)
#                 VALUES (%s, %s, %s, %s, %s)
#                 """, (
#                     seller_id,
#                     seller_info['sid'],
#                     seller_info['name'],
#                     seller_info['tradeMark'],
#                     seller_info['token']
#                     ))

#             week_ago = datetime.now() - timedelta(days=6)

#             cur.execute("""
#                 INSERT INTO seller_settings (
#                     seller_id, load_cards_stat, cards_stat_last_updated,
#                     load_orders, orders_last_updated,
#                     load_sales, sales_last_updated,
#                     load_adverts_stat, adverts_stat_last_updated,
#                     keywords_stat_last_updated,
#                     load_finances, finances_last_updated,
#                     load_remains, load_imcomes,
#                     incomes_last_updated, update_pipeline_data
#                 ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """, (
#                     seller_id,
#                     True, week_ago,
#                     True, week_ago,
#                     True, week_ago,
#                     True, week_ago,
#                     week_ago,
#                     True, week_ago,
#                     True, True,
#                     week_ago, True
#             ))
#         conn.commit()


# --- Main Initialization Entry Point
def init_databases(seller_info: dict, databases: list[dict]):
    logging.info('✨ Initialising databases...')
    # save_seller(seller_info, databases)
    create_schema(databases)
    # fill_data(seller_info, databases[0])
    logging.info('🎉 Databases initialised')
