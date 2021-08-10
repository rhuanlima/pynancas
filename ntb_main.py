#%%
from model.create_db import DB_Manager
import numpy as np
#%%

new_db = DB_Manager()
# %%
df = new_db.read_file('data/import/data.csv')
# %%
df_accounts = df[df['Nome'].isnull() == False][['Nome', 'Saldo atual']].copy()
# %%
df_accounts.reset_index(inplace=True)
del df_accounts['index']
df_accounts.info()
# %%
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x:x.replace('BRL',''))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x: x.replace('.',''))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].apply(lambda x: x.replace(',','.'))
df_accounts['Saldo atual'] = df_accounts['Saldo atual'].astype(float)
# %%
df_accounts.info()
# %%
df
# %%
