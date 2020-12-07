import os
import pathlib
from datetime import datetime

import pandas as pd

from mysql_conn import MySQL


def main():
    mysql_obj = setup_mysql()
    data = load_data(mysql_obj)
    pathlib.Path(os.path.join('..', 'data')).mkdir(parents=True, exist_ok=True)
    data.to_csv(os.path.join('..', 'data', '%s.csv' % datetime.today().strftime('%Y_%m_%d')), index=True, header=True)
    mysql_obj.connection.close()
    print('Data exported successfully!')


def load_df(data):
    df = pd.DataFrame(data)
    df.columns = ['high', 'low', 'adjusted_close', 'date', 'dollar', 'nome']
    df.set_index('date', inplace=True)
    df.dropna()
    stocks = df.sort_index(ascending=True)
    return stocks


def load_data(mysql_obj):
    query = """
    SELECT ta.alta, ta.baixa, ta.fechamento_ajustado, ta.data, tdr.fechamento AS dollar, inv.nome
    FROM tb_acao ta
        INNER JOIN tb_dolar_real tdr ON ta.data = tdr.data
        INNER JOIN tb_investimento inv ON ta.id_investimento = inv.id
    ORDER BY inv.nome;
    """
    data = mysql_obj.execute_read_query(query)
    stocks = load_df(data)
    return stocks


def setup_mysql():
    host = 'localhost'
    mysql_user = 'alunos'
    mysql_password = 'alunos'
    db_name = 'SISTEMA_INVESTIMENTO'
    mysql_obj = MySQL(host, mysql_user, mysql_password, db_name)
    return mysql_obj


if __name__ == '__main__':
    main()
