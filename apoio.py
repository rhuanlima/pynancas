# Criar uma nova conta
new_account = Account(des_account="Conta Pessoal")
session.add(new_account)
session.commit()

# Criar uma nova categoria
new_category = Category(des_category="Alimentação")
session.add(new_category)
session.commit()

# Criar uma nova subcategoria
new_subcategory = Subcategory(des_subcategory="Restaurante")
session.add(new_subcategory)
session.commit()


new_transaction = Transaction(
    dt_transaction="2023-11-05",
    vintage_transaction="2023-11-05",
    vintage_installment_card="2023-11-05",
    id_account=1,  # Substitua pelo ID da conta apropriada
    des_description="Descrição da transação",
    id_account_from=2,  # Substitua pelo ID da conta de origem apropriada
    id_account_to=3,  # Substitua pelo ID da conta de destino apropriada
    id_category=1,  # Substitua pelo ID da categoria apropriada
    id_subcategory=1,  # Substitua pelo ID da subcategoria apropriada
    vl_transaction=100.0,
    num_installments=1,
    num_total_installments=1,
    fl_consolidated=True,
)
session.add(new_transaction)
session.commit()


# Obter todas as transações
transactions = session.query(Account).all()
for transaction in transactions:
    print(transaction.des_account)
# Atualizar uma transação
transaction_to_update = session.query(Transaction).filter_by(id=1).first()
transaction_to_update.des_description = "Nova descrição"
session.commit()

# Excluir uma transação
transaction_to_delete = session.query(Transaction).filter_by(id=1).first()
session.delete(transaction_to_delete)
session.commit()
