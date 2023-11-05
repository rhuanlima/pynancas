from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.db_crud import Base, Account, Category, Subcategory, Transaction
from model.log import get_log

logger = get_log()

engine = create_engine("sqlite:///finance.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

logger.info("Iniciando o aplicativo")

session.close()
