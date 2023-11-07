from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    des_account = Column(String)
    fl_active = Column(Boolean, default=True)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    des_category = Column(String, unique=True)



class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    dt_transaction = Column(DateTime)
    vintage_transaction = Column(DateTime)
    vintage_installment_card = Column(DateTime)
    id_account = Column(Integer, ForeignKey("accounts.id"))
    account = relationship(Account, foreign_keys=[id_account])
    des_description = Column(String)
    id_account_from = Column(Integer, ForeignKey("accounts.id"))
    account_from = relationship(Account, foreign_keys=[id_account_from])
    id_account_to = Column(Integer, ForeignKey("accounts.id"))
    account_to = relationship(Account, foreign_keys=[id_account_to])
    id_category = Column(Integer, ForeignKey("categories.id"))
    category = relationship(Category)
    vl_transaction = Column(Float)
    num_installments = Column(Integer)
    num_total_installments = Column(Integer)
    fl_consolidated = Column(Boolean, default=False)
