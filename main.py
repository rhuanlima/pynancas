import model.db_crud as db
import model.log as log

logger = log.get_log()
banco = db.Banco()

banco.create_db()
logger.debug("Banco iniciado")

banco.close()
logger.debug("Banco encerrado")
