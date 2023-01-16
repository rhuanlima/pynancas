from sqlalchemy import create_engine

import model.import_data as dt_import
import model.log as log


class TableAsCreated(Exception):
    "Table as Created"
    pass


class Banco:
    def __init__(self):
        self.engine = create_engine("sqlite:///data/pynancas.sqlite3", echo=True)
        self.sqlite_connection = self.engine.connect()
        self.logger = log.get_log()

    def create_db(self, force=False):
        if force:
            self.sqlite_connection.execute("TRUNCATE TABLE tb_transactions")
            self.sqlite_connection.execute("TRUNCATE TABLE tb_categorias")
            self.sqlite_connection.execute("TRUNCATE TABLE tb_contas")
        df_money, df_categorias, df_contas = dt_import.import_db_gsheets(
            "data/original_db.csv"
        )
        # Criando base de dados se não existir
        try:
            df_money.to_sql("tb_transactions", self.sqlite_connection, if_exists="fail")
        except TableAsCreated:
            self.logger.debug("Table tb_transactions already create")
        try:
            df_categorias.to_sql(
                "tb_categorias", self.sqlite_connection, if_exists="fail"
            )
        except TableAsCreated:
            self.logger.debug("Table tb_categorias already create")
        try:
            df_contas.to_sql("tb_contas", self.sqlite_connection, if_exists="fail")
        except TableAsCreated:
            self.logger.debug("Table tb_contas already create")
        del [df_money, df_categorias, df_contas]

    def close(self):
        self.sqlite_connection.close()
        self.logger.debug("Connection closed")
