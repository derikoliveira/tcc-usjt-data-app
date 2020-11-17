from datetime import datetime

from constants import TABLE_NAMES
from models.investment import Investment
from models.variable_income import VariableIncome


class FixedIncome:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['fixed_income']

    def insert(self, date, due_date, annual_profitability, investment_id, minimum_investment, variable_income_id=None):
        name = f'{due_date} - {annual_profitability}'
        print(f'Inserting fixed income: {name}')
        if self.get_id(date, due_date, annual_profitability, investment_id, variable_income_id):
            print(f'Fixed income {name} already exists')
        else:
            if variable_income_id:
                insert = f"""
                INSERT INTO
                    {self.table_name} (data, data_vencimento, rendimento_fixo, id_investimento, id_rendimento_variavel, valor_minimo)
                VALUES
                    ('{date}', '{due_date}', {annual_profitability}, {investment_id}, {variable_income_id}, {minimum_investment})
                """
            else:
                insert = f"""
                INSERT INTO
                    {self.table_name} (data, data_vencimento, rendimento_fixo, id_investimento, valor_minimo)
                VALUES
                    ('{date}', '{due_date}', {annual_profitability}, {investment_id}, {minimum_investment})
                """
            self.mysql_obj.execute_query(insert)

    def get_id(self, date, due_date, annual_profitability, investment_id, variable_income_id=None):
        query = f"""
            SELECT
                id FROM {self.table_name}
            WHERE
                {self.table_name}.data = '{date}'
            AND
                {self.table_name}.data_vencimento = '{due_date}'
            AND
                {self.table_name}.rendimento_fixo = {annual_profitability}
            AND
                {self.table_name}.id_investimento = {investment_id}
            """
        if variable_income_id:
            query += f"""AND {self.table_name}.id_rendimento_variavel = {variable_income_id}"""
        fixed_income = self.mysql_obj.execute_read_query(query)
        if fixed_income:
            fixed_income_id = fixed_income[0][0]
            return fixed_income_id
        return None

    def insert_multiple(self, titulos_publicos_df):
        investment = Investment(self.mysql_obj)
        variable_income = VariableIncome(self.mysql_obj)
        today = datetime.today()

        for titulo_publico in titulos_publicos_df.itertuples():
            investment_id = investment.get_id(titulo_publico.title)
            try:
                minimum_investment = titulo_publico.minimum_investment
            except AttributeError:
                # Títulos para resgate, não têm investimento mínimo
                # https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm > "Resgatar"
                minimum_investment = 0.0

            if len(titulo_publico.annual_profitability) > 1:
                variable_income_id = variable_income.get_id_by_name(titulo_publico.annual_profitability[1])
                if not variable_income_id:
                    raise ValueError('TB_RENDIMENTO_VARIAVEL não encontrada, insira os valores')
                self.insert(
                    today,
                    titulo_publico.due_date,
                    titulo_publico.annual_profitability[0],
                    investment_id,
                    minimum_investment,
                    variable_income_id
                )
            else:
                self.insert(
                    today,
                    titulo_publico.due_date,
                    titulo_publico.annual_profitability[0],
                    investment_id,
                    minimum_investment
                )
