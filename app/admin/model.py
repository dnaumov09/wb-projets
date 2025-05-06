import os
from sqlalchemy import (
    Column, String, Boolean, BigInteger, Integer,
    ForeignKey, create_engine, UniqueConstraint
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Base class for declarative models
Base = declarative_base()

# ---------- Sellers Table ----------
class Seller(Base):
    __tablename__ = 'sellers'

    sid = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    trade_mark = Column(String, nullable=True)
    token = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=False)
    id = 1

    # Relationships
    users = relationship("SellerUser", back_populates="seller", cascade="all, delete-orphan")
    databases = relationship("SellerDatabase", back_populates="seller", cascade="all, delete-orphan")
    db_users = relationship("DatabaseUser", back_populates="seller", cascade="all, delete-orphan")


# ---------- Seller Users Table ----------
class SellerUser(Base):
    __tablename__ = 'seller_users'

    id = Column(BigInteger, primary_key=True)
    seller_sid = Column(String, ForeignKey('sellers.sid'), primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    tg_chat_id = Column(BigInteger)
    receive_sales = Column(Boolean, nullable=False, default=False)
    receive_supplies_statuses = Column(Boolean, nullable=False, default=False)

    # Relationships
    seller = relationship("Seller", back_populates="users")


# ---------- Seller Databases Table ----------
class SellerDatabase(Base):
    __tablename__ = 'seller_databases'

    host = Column(String, nullable=False, primary_key=True)
    port = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    seller_sid = Column(String, ForeignKey('sellers.sid'), primary_key=True)
    database_type = Column(String, primary_key=True)

    # Relationships
    seller = relationship("Seller", back_populates="databases")


# ---------- Database Users Table ----------
class DatabaseUser(Base):
    __tablename__ = 'database_users'

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    seller_sid = Column(String, ForeignKey('sellers.sid'), primary_key=True)
    database_type = Column(String, primary_key=True)

    # Relationships
    seller = relationship("Seller", back_populates="db_users")


# ---------- Database Configuration ----------
# --- Environment Variables for Admin DB
HOST = os.getenv("ADMIN_DB_HOST")
PORT = os.getenv("ADMIN_DB_PORT")
DB_NAME = os.getenv("ADMIN_DB_NAME")
USERNAME = os.getenv("ADMIN_DB_USERNAME")
PASSWORD = os.getenv("ADMIN_DB_PASSWORD")
DB_URL = f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"


engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
session = Session()
