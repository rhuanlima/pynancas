from datetime import datetime

import pandas as pd


def import_db_gsheets(db_path=None):
    """Função para importar dados do gsheets ou para criar a tabela em branco partindo de um dataframe pandas

    Args:
        db_path (_type_, optional): Path to database csv. Defaults to None.

    Returns:
        DataFrame: df_money
        DataFrame: df_categorias
        DataFrame: df_contas
    """
    if db_path:
        df_money = pd.read_csv(db_path, sep=";")

        df_money["Valor"] = df_money["Valor"].apply(
            lambda x: x.replace("(", "-")
            .replace(")", "")
            .replace(".", "")
            .replace(",", ".")
        )
        df_money["Valor"] = df_money["Valor"].astype(float)

        df_money.columns = [
            "data",
            "safra",
            "ciclo",
            "id_conta",
            "ds_conta",
            "ds_pagadores",
            "id_conta_recebida",
            "ds_conta_recebida",
            "id_conta_enviada",
            "ds_conta_enviada",
            "categoria",
            "subcategoria",
            "descricao",
            "valor",
            "nr_parcela",
            "total_parcela",
            "fl_consoliada",
            "fl_status_dia",
        ]

        # ajustando data
        df_money["data"] = df_money["data"].apply(
            lambda x: datetime.strptime(x, "%d/%m/%Y")
        )
        df_money["id_conta"] = df_money["id_conta"].astype("int64")
        df_money["id_conta_recebida"] = (
            df_money["id_conta_recebida"].fillna(0).astype("int64")
        )
        df_money["id_conta_enviada"] = (
            df_money["id_conta_enviada"].fillna(0).astype("int64")
        )
        df_money["safra"] = df_money["safra"].fillna(0).astype("int64")
        df_money["ciclo"] = df_money["ciclo"].fillna(0).astype("int64")

        # criando as contas com um ID e Descrição
        df_contas = (
            df_money[~df_money.duplicated(subset=["id_conta"])][
                ["id_conta", "ds_conta"]
            ]
            .sort_values(by="id_conta")
            .reset_index()
            .copy()
        )
        del df_contas["index"]

        # removendo campos descritivos da tabela e ficando apenas com os ID das contas
        del df_money["ds_conta"]
        del df_money["ds_conta_recebida"]
        del df_money["ds_conta_enviada"]

        # Criando um campo FATO com o descritivo da transação
        df_money["ds_fato"] = df_money["ds_pagadores"] + " | " + df_money["descricao"]
        del df_money["ds_pagadores"]
        del df_money["descricao"]

        # criando tabela de categorias e subcategorias
        df_categorias = (
            df_money[~df_money.duplicated(subset=["categoria"])]["categoria"]
            .sort_values()
            .reset_index()
            .copy()
        )
        del df_categorias["index"]
        df_categorias["id"] = df_categorias.index + 1
        df_categorias = df_categorias[["id", "categoria"]].copy()
        df_categorias["id_pai"] = 0
        df_categorias.columns = ["id", "ds_categoria", "id_pai"]

        # capturando as subcategorias na mesma tabela
        df_subcategorias = (
            df_money[~df_money.duplicated(subset=["categoria", "subcategoria"])][
                ["categoria", "subcategoria"]
            ]
            .sort_values(by="subcategoria")
            .reset_index()
            .copy()
        )
        del df_subcategorias["index"]

        df_subcategorias["idsub"] = df_subcategorias.index + df_categorias.shape[0] + 1

        df_subcategorias = pd.merge(
            df_subcategorias,
            df_categorias[["id", "ds_categoria"]],
            how="left",
            left_on="categoria",
            right_on="ds_categoria",
        )
        del df_subcategorias["ds_categoria"]
        del df_subcategorias["categoria"]

        df_subcategorias.columns = ["ds_categoria", "id", "id_pai"]

        df_categorias = pd.concat(
            [
                df_categorias[["id", "ds_categoria", "id_pai"]],
                df_subcategorias[["id", "ds_categoria", "id_pai"]],
            ]
        )

        # carregando os Ids das categorias
        df_money = pd.merge(
            df_money,
            df_categorias[df_categorias["id_pai"] == 0][["id", "ds_categoria"]],
            how="left",
            left_on="categoria",
            right_on="ds_categoria",
        ).copy()
        df_money.rename(columns={"id": "id_categoria"}, inplace=True)
        del df_money["ds_categoria"]
        df_money["key"] = (
            df_money["id_categoria"].astype(str) + " | " + df_money["subcategoria"]
        )

        df_categorias["key"] = (
            df_categorias["id_pai"].astype(str) + " | " + df_categorias["ds_categoria"]
        )

        df_money = pd.merge(
            df_money, df_categorias[["id", "key"]], how="left", on="key"
        )

        del df_money["key"]
        del df_money["categoria"]
        del df_money["subcategoria"]
        del df_categorias["key"]
        df_money.rename(columns={"id": "id_subcategoria"}, inplace=True)

    else:
        df_money = pd.DataFrame(
            {
                "data": pd.Series(dtype="datetime64[ns]"),
                "safra": pd.Series(dtype="int64"),
                "ciclo": pd.Series(dtype="int64"),
                "id_conta": pd.Series(dtype="int64"),
                "id_conta_recebida": pd.Series(dtype="int64"),
                "id_conta_enviada": pd.Series(dtype="int64"),
                "valor": pd.Series(dtype="float64"),
                "nr_parcela": pd.Series(dtype="int64"),
                "total_parcela": pd.Series(dtype="int64"),
                "fl_consoliada": pd.Series(dtype="int64"),
                "fl_status_dia": pd.Series(dtype="int64"),
                "ds_fato": pd.Series(dtype="object"),
                "id_categoria": pd.Series(dtype="int64"),
                "id_subcategoria": pd.Series(dtype="int64"),
            }
        )
        df_categorias = pd.DataFrame(
            {
                "id": pd.Series(dtype="int64"),
                "ds_categoria": pd.Series(dtype="object"),
                "id_pai": pd.Series(dtype="int64"),
            }
        )
        df_contas = pd.DataFrame(
            {
                "id_conta": pd.Series(dtype="int64"),
                "ds_conta": pd.Series(dtype="object"),
            }
        )

    return df_money, df_categorias, df_contas
