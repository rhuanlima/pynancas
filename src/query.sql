-- Contas iniciais
SELECT 
    Id, Name, OpeningBalance
FROM Accounts;

-- Categorias e subcategorias
SELECT
Id, Name, ParentCategoryId
FROM Categories;

-- Pagadores? para quem eu pago
SELECT 
Id, Name  
FROM Payees;

-- transações puras
SELECT *
--Id,
--AccountId,
--Date,
--Description,
--Amount,
--OriginalAmount,
--PayeeId,
--Notes
FROM Transactions WHERE TransactionType in (4,5);

with cte_transaction as (
SELECT
Id as id_transacao,
Date as dt_transacao,
AccountId as id_conta,
(select Name from Accounts where id = AccountId) as ds_conta,
(select Name from Payees where id = PayeeId) as ds_pagadores,
SenderAccountId as id_conta_recebida,
(case 
    when SenderAccountId is NOT NULL then 
        (select Name from Accounts where id = SenderAccountId) 
    else NULL
end) as ds_conta_recebida,
RecipientAccountId as id_conta_enviada,
(case 
    when RecipientAccountId is NOT NULL then 
        (select Name from Accounts where id = RecipientAccountId) 
    else NULL
end) as ds_conta_enviada,
(CASE
    when SenderAccountId is not null then 'T'
    when RecipientAccountId is not null then 'T'
    when Amount < 0 then 'D'
    when Amount >= 0 then 'C'
end) as tp_transacao,
(select CategoryId from CategoryAssigments where TransactionId = Transactions.Id) as id_categoria,
Description as ds_descricao,
Amount as vl_transacao,
Notes as ds_memo
from Transactions 
),

cte_base_final as (select 
id_transacao,
dt_transacao,
id_conta,
ds_conta,
ds_pagadores,
id_conta_recebida,
ds_conta_recebida,
id_conta_enviada,
ds_conta_enviada,
tp_transacao,
id_categoria,
(select Name from Categories where Id = id_categoria) as ds_categoria,
ds_descricao,
vl_transacao,
ds_memo
from cte_transaction),

saida as ( select * from cte_base_final)

create table if not EXISTS "tb_saida" (select * from saida);

