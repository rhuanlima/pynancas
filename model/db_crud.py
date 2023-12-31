from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    des_account = Column(String)
    fl_active = Column(Boolean, default=True)
    tp_account = Column(String)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    des_category = Column(String, unique=True)


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    dt_transaction = Column(DateTime)
    vintage_transaction = Column(Integer)
    vintage_installment_card = Column(Integer)
    id_account = Column(Integer, ForeignKey("accounts.id"))
    account = relationship(Account, foreign_keys=[id_account], lazy="joined")
    des_description = Column(String)
    id_account_from = Column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    account_from = relationship(Account, foreign_keys=[id_account_from], lazy="joined")
    id_account_to = Column(
        Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True
    )
    account_to = relationship(Account, foreign_keys=[id_account_to], lazy="joined")
    id_category = Column(Integer, ForeignKey("categories.id"))
    category = relationship(Category)
    vl_transaction = Column(Float)
    num_installments = Column(Integer)
    num_total_installments = Column(Integer)
    fl_consolidated = Column(Boolean, default=False)
