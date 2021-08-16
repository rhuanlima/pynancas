#%%
from model.create_db import DB_Manager
import numpy as np
import pandas as pd
pd.options.display.float_format = 'R${:,.2f}'.format
new_db = DB_Manager()
df = new_db.read_file('data/import/data.csv')
df_accounts = df[df['Nome'].isnull() == False][['Nome', 'Saldo atual']].copy()
df_accounts.reset_index(inplace=True)
del df_accounts['index']
df_accounts.info()
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x:x.replace('BRL',''))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x: x.replace('.',''))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x: x.replace(',','.'))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].astype(float)
df_accounts.reset_index(inplace=True)
df_accounts.rename(columns={'index':'id_account'}, inplace=True)
df_accounts.rename(columns={'Nome':'des_account'}, inplace=True)
df_accounts.rename(columns={'Saldo atual':'vlr_full_balance'}, inplace=True)
df_accounts
df_transactions = df[df['Nome'].isnull() == True][['Conta', 'Transferências', 'Descrição', 'Beneficiário', 'Categoria', 'Data', 'Tempo', 'Memo', 'Valor']].copy()
df_transactions.head()
df_transactions['dt_transaction'] = pd.to_datetime(df_transactions['Data'] + ' ' + df_transactions['Tempo'])
del df_transactions['Tempo']
del df_transactions['Data']
df_transactions['Valor'] = df_transactions['Valor'].apply(lambda x:x.replace('BRL',''))
df_transactions['Valor'] = df_transactions['Valor'].apply(lambda x: x.replace('.',''))
df_transactions['Valor'] = df_transactions['Valor'].apply(lambda x: x.replace(',','.'))
df_transactions['Valor'] = df_transactions['Valor'].astype(float)
df_transactions.rename(columns={'Conta':'des_account'}, inplace=True)
df_transactions = pd.merge(df_transactions, df_accounts[['id_account','des_account']], on='des_account', how='left')
df_transactions.rename(columns={'Valor':'balance'}, inplace=True)
df_transactions.rename(columns={'Memo':'des_info'}, inplace=True)
df_transactions.rename(columns={'Beneficiário':'des_benef'}, inplace=True)
df_transactions.rename(columns={'Categoria':'des_category'}, inplace=True)
df_transactions = pd.merge(df_transactions, df_accounts[['id_account','des_account']], left_on = 'Transferências', right_on='des_account', how='left')
df_transactions.rename(columns={'des_account_x':'des_account_from'}, inplace=True)
df_transactions.rename(columns={'id_account_x':'id_account_from'}, inplace=True)
df_transactions.rename(columns={'id_account_y':'id_account_to'}, inplace=True)
df_transactions.rename(columns={'des_account_y':'des_account_to'}, inplace=True)
del df_transactions['Transferências']
df_transactions.rename(columns={'Descrição':'des_transaction_old'}, inplace=True)
print(df_transactions.info())
df_transactions.head()
df_transactions.groupby(['id_account_from','des_account_from'])['balance'].sum()
dfa = df_transactions.groupby(['id_account_from','des_account_from']).agg({'balance':'sum', 'dt_transaction':'min'})
dfb = df_accounts.groupby(['id_account'])['vlr_full_balance'].sum().reset_index()
df_transactions_accounts = pd.merge(dfa, dfb, left_on = 'id_account_from', right_on='id_account', how='left')
df_transactions_accounts['open_balance'] = df_transactions_accounts['vlr_full_balance'] - df_transactions_accounts['balance']
df_transactions_accounts.info()
df_transactions_accounts.rename(columns={'id_account':'id_account_from'}, inplace=True)
df_transactions_accounts.rename(columns={'des_account':'des_account_from'}, inplace=True)
del df_transactions_accounts['balance']
del df_transactions_accounts['vlr_full_balance']
df_transactions_accounts.rename(columns={'opne_balance':'balance'}, inplace=True)
del df_transactions['des_account_from']
del df_transactions['des_account_to']
def make_transaction(id_account_from, id_account_to, balance):
    if not id_account_to != id_account_to:
        return 2  # Transferência
    elif balance < 0:
        return 1  # Saque
    else:
        return 0  # Deposito
df_transactions['id_transaction'] = df_transactions.apply(lambda x: make_transaction(x['id_account_from'], x['id_account_to'], x['balance']), axis=1)
# %%

df_transactions['des_info_bol'] = df_transactions['des_info'].isnull()
df_transactions['des_info'] = df_transactions.apply(lambda x: x['des_info'] if not x['des_info_bol'] else "", axis=1)
#del df_transactions['des_transaction_old']
#%%

df_analise = df_transactions[(df_transactions['des_info'] != "")].copy()
df_analise['bol_check'] = df_analise['des_info'].apply(lambda x: x.upper().find(' DE ') != -1)
df_analise[df_analise['bol_check'] == True]
# %%
df_transactions_accounts

df_transactions.head()

# %%
df_transactions.info()
# %%
