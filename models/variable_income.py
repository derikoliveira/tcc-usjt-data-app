from constants import TABLE_NAMES
from models.variable_income_type import VariableIncomeType


class VariableIncome:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['income_variable']

    def insert(self, value, id_tipo_rendimento_variavel):
        name = f'{value} - {id_tipo_rendimento_variavel}'
        print(f'Inserting income variable: {name}')
        if self.get_id(value, id_tipo_rendimento_variavel):
            print(f'Income variable {name} already exists')
        else:
            insert = f"""
            INSERT INTO
                {self.table_name} (valor, id_tipo_rendimento_variavel)
            VALUES
                ({value}, {id_tipo_rendimento_variavel})
            """
            self.mysql_obj.execute_query(insert)

    def get_id(self, value, id_tipo_rendimento_variavel):
        query = f"""
            SELECT id FROM {self.table_name}
            WHERE
                {self.table_name}.valor = {value}
            AND
                {self.table_name}.id_tipo_rendimento_variavel = {id_tipo_rendimento_variavel}
            """
        investment_type = self.mysql_obj.execute_read_query(query)
        if investment_type:
            investment_type_id = investment_type[0][0]
            return investment_type_id
        return None

    def get_id_by_name(self, name):
        variable_income_type = VariableIncomeType(self.mysql_obj)
        variable_income_type_id = variable_income_type.get_id(name)
        query = f"""
            SELECT id FROM
                {self.table_name}
            WHERE
                {self.table_name}.id_tipo_rendimento_variavel = {variable_income_type_id}
            """
        investment_type = self.mysql_obj.execute_read_query(query)
        if investment_type:
            investment_type_id = investment_type[0][0]
            return investment_type_id
        return None

    def insert_multiple(self, data_frame):
        variable_income_type = VariableIncomeType(self.mysql_obj)
        for titulo_publico in data_frame.itertuples():
            if len(titulo_publico.annual_profitability) > 1:
                variable_income_type_id = variable_income_type.get_id(titulo_publico.annual_profitability[1])
                self.insert(titulo_publico.annual_profitability[0], variable_income_type_id)
