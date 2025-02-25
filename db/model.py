import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DB_URL")

Base = declarative_base()
engine = create_engine(DB_URL, echo=False)

Session = sessionmaker(bind=engine)
session = Session()