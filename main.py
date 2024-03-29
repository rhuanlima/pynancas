# Import for Migrations
from datetime import datetime
from os import getenv
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_babel import Babel, Locale, format_currency
from sqlalchemy import case, create_engine, func
from sqlalchemy.orm import sessionmaker
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from model.db_crud import Account, Base, Category, Transaction, User
from model.log import get_log
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError


load_dotenv()

logger = get_log()

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Acesso negado!"

babel = Babel(app)
locale = Locale("pt_BR")
app.jinja_env.filters["format_currency"] = format_currency
app.config["BABEL_DEFAULT_LOCALE"] = "pt_BR"


DATABASE_URL = getenv("DATABASE_URL")
app.secret_key = getenv("secret_key")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

logger.info("Iniciando o aplicativo")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=50)]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, field):
        session = Session()
        if session.query(User).filter_by(username=field.data).first():
            raise ValidationError("Username already taken. Choose a different one.")
        session.close()


@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(int(user_id))
    session.close()
    return user


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)

        session = Session()
        session.add(new_user)
        session.commit()
        session.close()
        flash("Your account has been created! You are now able to log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        session = Session()
        user = session.query(User).filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Credenciais inválidas. Tente novamente.", "error")
        session.close()
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Accounts Crud
@app.route("/accounts")
@login_required
def pg_accounts():
    session = Session()
    accounts = (
        session.query(Account)
        .order_by(Account.fl_active.desc())
        .order_by(Account.des_account)
        .all()
    )
    session.close()
    return render_template("accounts.html", accounts=accounts)


@app.route("/edit_account/<int:id>", methods=["GET", "POST"])
@login_required
def edit_account(id):
    session = Session()
    account = session.query(Account).get(id)

    if request.method == "POST":
        # Atualiza o nome da conta com base no formulário enviado
        new_account_name = request.form.get("new_account_name")
        account.des_account = new_account_name
        account.tp_account = request.form.get("tp_account")
        session.commit()
        session.close()
        flash("Conta alterada com sucesso!")
        return redirect(url_for("pg_accounts"))

    session.close()
    return render_template("edit_account.html", account=account)


@app.route("/deactivate_account/<int:id>")
@login_required
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
@login_required
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


@app.route("/consolidate_transaction/<int:id>")
@app.route("/consolidate_transaction/<int:id>/<int:ac_filter>")
@login_required
def consolidate_transaction(id, ac_filter=None):
    logger.info(f"Consolidando: {ac_filter}")
    session = Session()
    transaction = session.query(Transaction).get(id)

    # Ativa a conta
    transaction.fl_consolidated = True
    session.commit()
    session.close()
    flash(f"Transação {id} foi Consolidada!")
    if ac_filter is None:
        return redirect(url_for("pg_transactions"))
    return redirect(url_for("pg_transactions", ac_filter=ac_filter))


@app.route("/unconsolidate_transaction/<int:id>")
@app.route("/unconsolidate_transaction/<int:id>/<int:ac_filter>")
@login_required
def unconsolidate_transaction(id, ac_filter=None):
    session = Session()
    transaction = session.query(Transaction).get(id)

    # Ativa a conta
    transaction.fl_consolidated = False
    session.commit()
    session.close()
    flash(f"Transação {id} não foi consolidada!")
    if ac_filter is None:
        return redirect(url_for("pg_transactions"))
    return redirect(url_for("pg_transactions", ac_filter=ac_filter))


@app.route("/consolidate_transfer/<int:id>")
@login_required
def consolidate_transfer(id):
    session = Session()
    transaction = session.query(Transaction).get(id)
    transaction.fl_consolidated = True
    session.commit()
    session.close()
    flash(f"Transação {id} foi Consolidada!")
    return redirect(url_for("pg_transfers"))


@app.route("/unconsolidate_transfer/<int:id>")
@login_required
def unconsolidate_transfer(id):
    session = Session()
    transaction = session.query(Transaction).get(id)
    transaction.fl_consolidated = False
    session.commit()
    session.close()
    flash(f"Transação {id} não foi consolidada!")
    return redirect(url_for("pg_transfers"))


@app.route("/create_account", methods=["POST"])
@login_required
def create_account():
    session = Session()
    des_account = request.form.get("account_name")
    new_account = Account(
        des_account=des_account, tp_account=request.form.get("tp_account")
    )
    session.add(new_account)
    session.commit()
    session.close()
    return redirect(url_for("pg_accounts"))


# Category Crud
@app.route("/categories")
@login_required
def pg_categories():
    session = Session()
    categories = session.query(Category).all()
    session.close()
    return render_template("categories.html", categories=categories)


@app.route("/create_category", methods=["POST"])
@login_required
def create_category():
    session = Session()
    des_category = request.form.get("category_name")
    new_category = Category(des_category=des_category)
    session.add(new_category)
    session.commit()
    session.close()
    return redirect(url_for("pg_categories"))


@app.route("/edit_category/<int:id>", methods=["GET", "POST"])
@login_required
def edit_category(id):
    session = Session()
    category = session.query(Category).get(id)

    if request.method == "POST":
        new_category_name = request.form.get("new_category_name")
        category.des_category = new_category_name
        session.commit()
        session.close()
        flash("Categoria alterada com sucesso!")
        return redirect(url_for("pg_categories"))

    session.close()
    return render_template("edit_category.html", category=category)


# tansaction
@app.route("/transactions")
@app.route("/transactions/<int:ac_filter>", methods=["GET", "POST"])
@login_required
def pg_transactions(ac_filter=None):
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

    transactions = (
        session.query(Transaction).order_by(Transaction.id.desc()).limit(10).all()
    )

    if ac_filter is not None:
        transactions = (
            session.query(Transaction)
            .filter(Transaction.id_account == int(ac_filter))
            .order_by(Transaction.id.desc())
            .limit(10)
            .all()
        )

    accounts = session.query(Account).filter(Account.fl_active == True).all()
    categories = session.query(Category).all()
    session.close()
    return render_template(
        "transaction.html",
        transactions=transactions,
        accounts=accounts,
        categories=categories,
        total_balances=total_balances,
        ac_filter=ac_filter,
    )


@app.route("/create_transaction", methods=["POST"])
@login_required
def create_transaction():
    session = Session()
    dt_transaction = datetime.strptime(request.form.get("dt_transaction"), "%Y-%m-%d")
    vintage_transaction = dt_transaction.year * 100 + dt_transaction.month
    nr_installments = int(request.form.get("num_total_installments"))
    installment = 1
    while installment <= nr_installments:
        # Obtenha os dados do formulário e crie uma nova transação
        if request.form.get("fl_next_month"):
            vintage_installment_card = (
                dt_transaction + relativedelta(months=(installment - 1))
            ).year * 100 + (
                dt_transaction + relativedelta(months=(installment - 1))
            ).month
        else:
            vintage_installment_card = (
                dt_transaction + relativedelta(months=installment)
            ).year * 100 + (dt_transaction + relativedelta(months=installment)).month

        print(
            f"Vintage {vintage_installment_card} - data {dt_transaction}data + {installment-1} = {dt_transaction + relativedelta(months=(installment-1))}"
        )
        new_transaction = Transaction(
            dt_transaction=dt_transaction,
            # dt_transaction=request.form.get("dt_transaction"),
            vintage_transaction=vintage_transaction,
            vintage_installment_card=vintage_installment_card,
            id_account=int(request.form.get("id_account")),
            des_description=request.form.get("des_description"),
            # id_account_from=int(request.form.get("id_account_from")),
            # id_account_to=int(request.form.get("id_account_to")),
            id_category=int(request.form.get("id_category")),
            vl_transaction=float(request.form.get("vl_transaction")),
            num_installments=installment,
            num_total_installments=nr_installments,
            fl_consolidated=bool(request.form.get("fl_consolidated")),
        )
        session.add(new_transaction)
        session.commit()
        installment += 1
    session.close()
    if request.form.get("ac_filter") != "None":
        return redirect(
            url_for("pg_transactions", ac_filter=request.form.get("ac_filter"))
        )
    return redirect(url_for("pg_transactions"))


@app.route("/transfer")
@login_required
def pg_transfers():
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
    categories = (
        session.query(Category).filter(Category.des_category == "Transferência").all()
    )
    try:
        transactions = (
            session.query(Transaction)
            .filter(Transaction.id_category == categories[0].id)
            .order_by(Transaction.id.desc())
            .limit(10)
            .all()
        )
    except Exception as e:
        logger.error(e)
        transactions = ()
    accounts = session.query(Account).filter(Account.fl_active == True).all()
    session.close()
    return render_template(
        "transfer.html",
        transactions=transactions,
        accounts=accounts,
        categories=categories,
        total_balances=total_balances,
    )


@app.route("/create_transfer", methods=["POST"])
@login_required
def create_transfer():
    session = Session()
    dt_transaction = datetime.strptime(request.form.get("dt_transaction"), "%Y-%m-%d")
    vintage_transaction = dt_transaction.year * 100 + dt_transaction.month
    nr_installments = 1
    installment = 1

    new_transaction = Transaction(
        dt_transaction=dt_transaction,
        # dt_transaction=request.form.get("dt_transaction"),
        vintage_transaction=vintage_transaction,
        vintage_installment_card=vintage_transaction,
        id_account=int(request.form.get("id_account_from")),
        des_description=request.form.get("des_description"),
        id_account_from=int(request.form.get("id_account_from")),
        id_account_to=int(request.form.get("id_account_to")),
        id_category=int(request.form.get("id_category")),
        vl_transaction=float(request.form.get("vl_transaction")),
        num_installments=installment,
        num_total_installments=nr_installments,
        fl_consolidated=bool(request.form.get("fl_consolidated")),
    )
    session.add(new_transaction)
    session.commit()

    new_transaction = Transaction(
        dt_transaction=dt_transaction,
        # dt_transaction=request.form.get("dt_transaction"),
        vintage_transaction=vintage_transaction,
        vintage_installment_card=vintage_transaction,
        id_account=int(request.form.get("id_account_to")),
        des_description=request.form.get("des_description"),
        id_account_from=int(request.form.get("id_account_from")),
        id_account_to=int(request.form.get("id_account_to")),
        id_category=int(request.form.get("id_category")),
        vl_transaction=float(request.form.get("vl_transaction")) * -1,
        num_installments=installment,
        num_total_installments=nr_installments,
        fl_consolidated=bool(request.form.get("fl_consolidated")),
    )
    session.add(new_transaction)
    session.commit()
    session.close()
    return redirect(url_for("pg_transfer"))


@app.route("/delete_transaction/<int:id>", methods=["GET", "POST"])
@login_required
def delete_transaction(id):
    session = Session()
    tansaction = session.query(Transaction).filter(Transaction.id == id).one()
    session.delete(tansaction)
    session.commit()
    session.close()
    flash("Transação excluida com sucesso!")
    return redirect(url_for("pg_transactions"))


@app.route("/edit_transaction/<int:id>", methods=["GET", "POST"])
@login_required
def edit_transaction(id):
    session = Session()
    transaction = session.query(Transaction).filter(Transaction.id == id).one()
    accounts = session.query(Account).filter(Account.fl_active == True).all()
    categories = session.query(Category).all()
    if request.method == "POST":
        transaction.dt_transaction = datetime.strptime(
            request.form.get("dt_transaction"), "%Y-%m-%d"
        )
        transaction.vintage_transaction = int(request.form.get("vintage_transaction"))
        transaction.vintage_installment_card = int(
            request.form.get("vintage_installment_card")
        )
        transaction.id_account = int(request.form.get("id_account"))
        transaction.des_description = request.form.get("des_description")
        try:
            transaction.id_account_from = int(request.form.get("id_account_from"))
        except Exception as e:
            logger.error(e)
            transaction.id_account_from = request.form.get("id_account_from")
        try:
            transaction.id_account_to = int(request.form.get("id_account_to"))
        except Exception as e:
            logger.error(e)
            transaction.id_account_to = request.form.get("id_account_to")
        transaction.id_category = int(request.form.get("id_category"))
        transaction.vl_transaction = float(request.form.get("vl_transaction"))
        transaction.num_installments = int(request.form.get("num_installments"))
        transaction.num_total_installments = int(
            request.form.get("num_total_installments")
        )
        transaction.fl_consolidated = bool(request.form.get("fl_consolidated"))
        session.commit()
        flash("Transação editada com sucesso!")
        return redirect(url_for("edit_transaction", id=id))
    session.close()
    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        accounts=accounts,
        categories=categories,
    )


@app.route("/creditcard")
@login_required
def rel_creditcard():
    session = Session()
    accounts = (
        session.query(Account)
        .where(Account.tp_account == "c")
        .where(Account.fl_active == True)
        .all()
    )
    data_atual = datetime.now()
    vnt_list = []
    for i in range(-3, 10):
        dt_in = data_atual + relativedelta(months=i)
        vnt_list.append(int(f"{dt_in.year}{dt_in.month:02}"))

    total_balances = (
        session.query(
            Account.id.label("id"),
            Account.des_account.label("account"),
            Transaction.vintage_installment_card,
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
        .filter(Account.tp_account == "c")
        .filter(Account.fl_active == True)
        .filter(Transaction.vl_transaction < 0)
        .filter(Transaction.vintage_installment_card >= vnt_list[0])
        .filter(Transaction.vintage_installment_card <= vnt_list[len(vnt_list) - 1])
        .group_by(Account.id)
        .group_by(Transaction.vintage_installment_card)
        .order_by(Account.des_account)
        .order_by(Transaction.vintage_installment_card)
        .all()
    )
    df = pd.DataFrame(
        [
            (
                account.id,
                account.account,
                account.vintage_installment_card,
                account.total_balance,
                account.consolidated_balance,
            )
            for account in total_balances
        ],
        columns=[
            "id",
            "account",
            "vintage_installment_card",
            "total_balance",
            "consolidated_balance",
        ],
    )
    df = df.pivot_table(
        index="account",
        columns="vintage_installment_card",
        values="consolidated_balance",
        aggfunc="first",
    )
    df = df.fillna(0)
    df.loc["Total"] = df.sum()
    session.close()
    return render_template(
        "creditcard.html",
        accounts=accounts,
        total_balances=total_balances,
        vnt_list=vnt_list,
        df=df,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
