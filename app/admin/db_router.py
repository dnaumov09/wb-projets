from enum import Enum

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from clickhouse_driver import Client

from admin.db_api import get_sid_db_config
from db.model.seller import Seller


class Database(Enum):
    POSTGRES = 'POSTGRES'
    CLICKHOUSE = 'CLICKHOUSE'


@lru_cache(maxsize=128)
def _get_db_connection(seller: Seller, database: Database):
    config = get_sid_db_config(seller.sid, database.name)
    if database == Database.POSTGRES:
        #POSTGRES SESSION
        db_url = (
            f"postgresql+psycopg2://{config['username']}:{config['password']}"
            f"@{config['host']}:{config['port']}/{config['dbname']}"
        )
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        return Session()
    else:
        #CLICKHOUSE CLIENT
        return Client(
            host=config['host'], 
            port=config['port'], 
            user=config['username'], 
            password=config['password'], 
            database=config['dbname']
        )
        
    

def get_session(seller: Seller) -> Session:
    return _get_db_connection(seller, Database.POSTGRES)


def get_client(seller: Seller) -> Client:
    return _get_db_connection(seller, Database.CLICKHOUSE)