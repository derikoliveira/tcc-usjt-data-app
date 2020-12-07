from constants import TABLE_NAMES


class VariableIncomeType:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['income_variable_type']

    def insert(self, name):
        print(f'Inserting income variable type: {name}')
        if self.get_id(name):
            print(f'Income variable type {name} already exists')
        else:
            insert = f"""INSERT INTO {self.table_name} (nome) VALUES ('{name}')"""
            self.mysql_obj.execute_query(insert)

    def get_id(self, name):
        query = f"""SELECT id FROM {self.table_name} where {self.table_name}.nome = '{name}'"""
        investment_type = self.mysql_obj.execute_read_query(query)
        if investment_type:
            investment_type_id = investment_type[0][0]
            return investment_type_id
        return None

    def insert_multiple(self, data_frame):
        for annual_profitability in data_frame:
            if len(annual_profitability) > 1:
                self.insert(annual_profitability[1])
