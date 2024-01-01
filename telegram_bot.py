import logging

from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import psycopg2
from os import getenv
from dotenv import load_dotenv
from sqlalchemy import case, create_engine, func
from sqlalchemy.orm import sessionmaker
from model.db_crud import Account, Base, Category, Transaction, User
from tabulate import tabulate

load_dotenv()

TOKEN = getenv("TOKEN_TELEGRAM")
DATABASE_URL = getenv("DATABASE_URL")
USER_ID = getenv("USER_ID")
# Conexão com o banco de dados
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.id}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def saldo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session = Session()
    total_balances = (
        session.query(
            Account.id.label("id"),
            Account.des_account.label("account"),
            func.coalesce(func.sum(Transaction.vl_transaction), 0).label(
                "total_balance"
            ),
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.fl_consolidated, Transaction.vl_transaction),
                        else_=0,
                    )
                ),
                0,
            ).label("consolidated_balance"),
        )
        .join(Transaction, Transaction.id_account == Account.id)
        .filter(Account.fl_active == True)
        .group_by(Account.id)
        .all()
    )
    session.close()
    data = [
        (balance.account, f"{balance.consolidated_balance:.2f}")
        for balance in total_balances
    ]
    table = tabulate(data, headers=["Account", "Balance"], tablefmt="grid")
    user = update.effective_user
    if user.id == int(USER_ID):
        await update.message.reply_text(f"Saldo:\n{table}")
    else:
        await update.message.reply_text("Quem é você?")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saldo", saldo))
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
