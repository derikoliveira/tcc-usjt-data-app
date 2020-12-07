from constants import TABLE_NAMES
from models.dim_time import DimTime


class FactStock:
    table_name = TABLE_NAMES['fact_stock']

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.df = None

    def get_growth(self, investment_id, dim_time_id):
        query = f"""
        SELECT
            crescimento, crescimento_porcentagem
        FROM
            {self.table_name}
        WHERE
            {self.table_name}.id_investimento = {investment_id}
        AND
            {self.table_name}.id_tempo = {dim_time_id}
        """
        return self.mysql_obj.execute_read_query(query)

    def insert(self, investment_id, dim_time_id, growth, growth_percentage):
        if not self.get_growth(investment_id, dim_time_id):
            insert = f"""
                INSERT INTO
                    {self.table_name} (id_investimento, id_tempo, crescimento, crescimento_porcentagem)
                VALUES
                    ({investment_id}, {dim_time_id}, {growth}, {growth_percentage})
            """
            self.mysql_obj.execute_query(insert)

    def insert_multiple(self, fact_stock_data_frame):
        dim_time = DimTime(self.mysql_obj)
        for fact_stock in fact_stock_data_frame.itertuples():
            dim_time_id = dim_time.get_id(fact_stock.date)
            self.insert(fact_stock.investment_id, dim_time_id, fact_stock.growth, fact_stock.growth_percentage)
