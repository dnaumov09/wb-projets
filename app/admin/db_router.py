from enum import Enum

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from clickhouse_driver import Client

from .model import Seller


class Database(Enum):
    POSTGRES = 'POSTGRES'
    CLICKHOUSE = 'CLICKHOUSE'


def _get_db_connection(seller: Seller, database: Database):
    db = next((db for db in seller.databases if db.database_type == database.name), None)
    usr = next((usr for usr in seller.db_users if usr.database_type == database.name), None)
    if database == Database.POSTGRES:
        #POSTGRES SESSION
        db_url = (
            f"postgresql+psycopg2://{usr.username}:{usr.password}"
            f"@{db.host}:{db.port}/{db.name}"
        )
        engine = create_engine(
            db_url,
            pool_pre_ping=True,          # проверка живости коннекта
            pool_recycle=1800,           # раз в 30 мин рециклим
            pool_size=5,
            max_overflow=10,
            connect_args={
                "application_name": "wb-projets",
                # TCP keepalives — помогают обнаружить разрывы сети
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                # Дополнительные настройки для стабильности
                "connect_timeout": 30,      # таймаут подключения
                "options": "-c statement_timeout=300000",  # 5 минут на запрос
                "options": "-c idle_in_transaction_session_timeout=300000",  # 5 минут на транзакцию
            },
        )
        Session = sessionmaker(bind=engine)
        return Session()
    else:
        #CLICKHOUSE CLIENT
        return Client(
            host=db.host, 
            port=db.port, 
            database=db.name,
            user=usr.username, 
            password=usr.password
        )
    

@lru_cache
def get_session(seller: Seller) -> Session:
    return _get_db_connection(seller, Database.POSTGRES)


@lru_cache
def get_client(seller: Seller) -> Client:
    return _get_db_connection(seller, Database.CLICKHOUSE)