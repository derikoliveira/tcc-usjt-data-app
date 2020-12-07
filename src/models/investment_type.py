from constants import TABLE_NAMES


class InvestmentType:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['investment_type']

    def insert(self, name):
        print(f'Inserting investment type: {name}')
        if self.get_id(name):
            print(f'Investment type {name} already exists')
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
