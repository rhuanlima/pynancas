from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from model.db_crud import Base, Account, Category, Transaction
from model.log import get_log
from flask import Flask, render_template, request, redirect, url_for, flash

logger = get_log()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
engine = create_engine("sqlite:///data/pynance.sqlite")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

logger.info("Iniciando o aplicativo")


@app.route("/")
def index():
    session = Session()

    # Obtém o total do saldo nas contas ativas considerando todas as transações, agrupado por conta
    total_balances = (
        session.query(
            Account.des_account,
            func.sum(Transaction.vl_transaction).label("total_balance"),
        )
        .join(Transaction, Transaction.id_account == Account.id)
        .filter(Account.fl_active == True)
        .group_by(Account.id)
        .all()
    )

    session.close()

    return render_template("index.html", total_balances=total_balances)


@app.route("/accounts")
def pg_accounts():
    session = Session()
    accounts = session.query(Account).all()
    session.close()
    return render_template("accounts.html", accounts=accounts)


@app.route("/edit_account/<int:id>", methods=["GET", "POST"])
def edit_account(id):
    session = Session()
    account = session.query(Account).get(id)

    if request.method == "POST":
        # Atualiza o nome da conta com base no formulário enviado
        new_account_name = request.form.get("new_account_name")
        account.des_account = new_account_name
        session.commit()
        session.close()
        flash("Conta alterada com sucesso!")
        return redirect(url_for("pg_accounts"))

    session.close()
    return render_template("edit_account.html", account=account)


@app.route("/deactivate_account/<int:id>")
def deactivate_account(id):
    session = Session()
    account = session.query(Account).get(id)

    # Desativa a conta
    account.fl_active = False
    account_name = account.des_account
    session.commit()
    session.close()
    flash(f"Conta {account_name} foi desativada!")
    return redirect(url_for("pg_accounts"))


@app.route("/activate_account/<int:id>")
def activate_account(id):
    session = Session()
    account = session.query(Account).get(id)

    # Ativa a conta
    account.fl_active = True
    account_name = account.des_account
    session.commit()
    session.close()
    flash(f"Conta {account_name} foi ativada!")
    return redirect(url_for("pg_accounts"))


@app.route("/create_account", methods=["POST"])
def create_account():
    session = Session()
    des_account = request.form.get("account_name")
    new_account = Account(des_account=des_account)
    session.add(new_account)
    session.commit()
    session.close()
    return redirect(url_for("pg_accounts"))


@app.route("/categorias")
def pg_categories():
    session = Session()
    categories = session.query(Category).all()
    session.close()
    return render_template("categories.html", categories=categories)


@app.route("/create_category", methods=["POST"])
def create_category():
    session = Session()
    des_category = request.form.get("category_name")
    new_category = Category(des_category=des_category)
    session.add(new_category)
    session.commit()
    session.close()
    return redirect(url_for("index"))


@app.route("/create_transaction", methods=["POST"])
def create_transaction():
    session = Session()
    # Obtenha os dados do formulário e crie uma nova transação
    new_transaction = Transaction(
        dt_transaction=request.form.get("dt_transaction"),
        vintage_transaction=request.form.get("vintage_transaction"),
        vintage_installment_card=request.form.get("vintage_installment_card"),
        id_account=int(request.form.get("id_account")),
        des_description=request.form.get("des_description"),
        id_account_from=int(request.form.get("id_account_from")),
        id_account_to=int(request.form.get("id_account_to")),
        id_category=int(request.form.get("id_category")),
        vl_transaction=float(request.form.get("vl_transaction")),
        num_installments=int(request.form.get("num_installments")),
        num_total_installments=int(request.form.get("num_total_installments")),
        fl_consolidated=bool(request.form.get("fl_consolidated")),
    )
    session.add(new_transaction)
    session.commit()
    session.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
