import src.import_data as dt_import 
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/pynancas.sqlite3", echo=True)
sqlite_connection = engine.connect()

df_money, df_categorias, df_contas = dt_import.import_db_gsheets("data/original_db.csv")

df_money.to_sql('tb_transactions', sqlite_connection, if_exists="fail")
df_categorias.to_sql('tb_categorias', sqlite_connection, if_exists="fail")
df_contas.to_sql('tb_contas', sqlite_connection, if_exists="fail")
sqlite_connection.close()
