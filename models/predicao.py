from constants import TABLE_NAMES


class Prediction:
    table_name = TABLE_NAMES['prediction']

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.df = None

    def insert(self, date, value, investment_id):
        insert = f"""
            INSERT INTO
                {self.table_name} (data, valor, id_investimento)
            VALUES
                ('{date}', {value}, {investment_id})
        """
        self.mysql_obj.execute_query(insert)

    def insert_multiple(self, prediction_df, investment_id):
        for index, prediction in prediction_df.iterrows():
            self.insert(index, prediction.adjusted_close, investment_id)
