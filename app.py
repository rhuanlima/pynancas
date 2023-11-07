from flask import Flask, render_template, request, redirect, url_for
from finance_manager import Account, Category, Subcategory, Transaction
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name)

engine = create_engine('sqlite:///finance.db')
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    session = Session()
    des_account = request.form.get('account_name')
    new_account = Account(des_account=des_account)
    session.add(new_account)
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/create_category', methods=['POST'])
def create_category():
    session = Session()
    des_category = request.form.get('category_name')
    new_category = Category(des_category=des_category)
    session.add(new_category)
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/create_subcategory', methods=['POST'])
def create_subcategory():
    session = Session()
    des_subcategory = request.form.get('subcategory_name')
    new_subcategory = Subcategory(des_subcategory=des_subcategory)
    session.add(new_subcategory)
    session.commit()
    session.close()
    return redirect(url_for('index'))

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    session = Session()
    # Obtenha os dados do formulário e crie uma nova transação
    new_transaction = Transaction(
        dt_transaction=request.form.get('dt_transaction'),
        vintage_transaction=request.form.get('vintage_transaction'),
        vintage_installment_card=request.form.get('vintage_installment_card'),
        id_account=int(request.form.get('id_account')),
        des_description=request.form.get('des_description'),
        id_account_from=int(request.form.get('id_account_from')),
        id_account_to=int(request.form.get('id_account_to')),
        id_category=int(request.form.get('id_category')),
        id_subcategory=int(request.form.get('id_subcategory')),
        vl_transaction=float(request.form.get('vl_transaction')),
        num_installments=int(request.form.get('num_installments')),
        num_total_installments=int(request.form.get('num_total_installments')),
        fl_consolidated=bool(request.form.get('fl_consolidated'))
    )
    session.add(new_transaction)
    session.commit()
    session.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
