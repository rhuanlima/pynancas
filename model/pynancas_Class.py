import datetime
import os
import sys
from peewee import *
from readchar import readchar
from collections import OrderedDict

db = SqliteDatabase("data/pynancas.db")


class Account(Model):
    id_account = AutoField()
    name = CharField(max_length=255)
    timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


class Transaction(Model):
    id_transaction = BigAutoField()
    name = CharField(max_length=255)
    dt_transaction = CharField(max_length=10)
    timestamp = DateTimeField(default=datetime.datetime.now)
    value = FloatField()
    id_account = ForeignKeyField(Account, "id_account")

    class Meta:
        database = db


def close():
    db.close()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def initialize():
    db.connect()
    db.create_tables([Transaction, Account], safe=True)


def show_last(entries):
    for transaction in entries:
        print(
            f"{transaction.id_transaction}) {transaction.name} - R${transaction.value}"
        )


def menu_loop():
    choice = None
    index = 0
    entries = Transaction.select().order_by(Transaction.timestamp.desc())
    while choice != "q":
        if len(entries) != 0:
            show_last(entries)
            print("\n" + "=" * 40 + "\n")
            print("Previous/Next: p/n \n")
        for key, value in main_menu.items():
            print("{}) {}".format(key, value.__doc__))
        print("q) Quit")
        print("\nAction: ", end="")
        choice = readchar()

        if choice in main_menu:
            try:
                main_menu[choice](index, entries)
            except ZeroDivisionError:
                continue
            # update entries after operations
            entries = Transaction.select().order_by(Transaction.timestamp.asc())

        elif choice == "n":
            index += 1
        elif choice == "p":
            index -= 1


def add_account(index, entries):
    """Nova Conta"""
    clear()
    print("Nova Conta")
    new_account = input("\nNome: ")
    if len(new_account) < 3:
        clear()
        print("***ERRO: Insira um nome com 3 ou mais caracteres!***\n\n")
        return None
    ret = Account.create(name=new_account)
    print(ret)


def add_credit(index, entries):
    """Nova transação de Crédito"""
    clear()

    print("Credito")

    for account in Account.select():
        print(f"{account.id_account}) {account.name}")
    try:
        id_account = int(input("\nConta: "))
    except:
        clear()
        print("***ERRO: Selecione uma conta***\n\n")
        return None

    name = input("\nNome: ")
    if len(name) < 3:
        clear()
        print("***ERRO: Insira um nome com 3 ou mais caracteres!***\n\n")
        return None

    dt_transaction = input("\nData(dd/mm/aaaa): ")
    if not check_date(dt_transaction):
        clear()
        print("***ERRO: Data incorreta!***\n\n")
        return None

    try:
        value = float(input("\nValor(000.00): "))
    except:
        clear()
        print('***ERRO: Valor inválido, utilize "." como marcador decimal!***\n\n')
        return None

    Transaction.create(
        name=name, dt_transaction=dt_transaction, value=value, id_account=id_account
    )


def check_date(dt):
    for i, j in enumerate(dt):
        if i == 2 and j != "/":
            return False
        elif i == 5 and j != "/":
            return False
        elif j not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "/"]:
            return False
    if len(dt) == 10:
        return True
    return False


def add_debit(index, entries):
    """Nova transação de Débito"""
    clear()
    print("Debito")


def add_transfer(index, entries):
    """Nova Transferencia"""
    clear()
    print("transferencia")


main_menu = OrderedDict(
    [("a", add_account), ("c", add_credit), ("d", add_debit), ("t", add_transfer)]
)
