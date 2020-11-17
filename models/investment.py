from constants import TABLE_NAMES


class Investment:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['investment']

    def insert(self, name, investment_type_id):
        print(f'Inserting investment: {name}')
        if self.get_id(name):
            print(f'Investment {name} already exists')
        else:
            insert = f"""
                INSERT INTO
                    {self.table_name} (nome, id_tipo_investimento)
                VALUES
                    ('{name}', {investment_type_id})
            """
            self.mysql_obj.execute_query(insert)

    def get_id(self, name):
        query = f"""SELECT id FROM {self.table_name} where {self.table_name}.nome = '{name}'"""
        investment = self.mysql_obj.execute_read_query(query)
        if investment:
            investment_id = investment[0][0]
            return investment_id
        return None

    def get_all_by_ids(self, ids):
        ids_str = ''
        for id_investment in ids:
            if not ids_str:
                ids_str += f'{str(id_investment)}'
            else:
                ids_str += f', {str(id_investment)}'
        query = f"""SELECT id, nome FROM {self.table_name} WHERE id IN ({ids_str})"""
        return self.mysql_obj.execute_read_query(query)

    def get_all_by_investment_type_id(self, investment_type_id):
        query = f"""
            SELECT id from tb_investimento where {self.table_name}.id_tipo_investimento = {investment_type_id};
        """
        return self.mysql_obj.execute_read_query(query)
