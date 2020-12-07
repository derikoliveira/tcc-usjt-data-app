from constants import TABLE_NAMES


class Stock:

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['stock']

    def get_close_adjusted_and_investment_id(self, date):
        query = f"""
        SELECT
            fechamento_ajustado, id_investimento
        FROM
            {self.table_name}
        WHERE
            {self.table_name}.data = '{date}'
        """
        return self.mysql_obj.execute_read_query(query)

    def get_all_by_investment_id(self, investment_id):
        query = f"""SELECT 
                alta, baixa, fechamento_ajustado, data
            FROM
                {self.table_name}
            WHERE
                id_investimento = {investment_id};
        """
        return self.mysql_obj.execute_read_query(query)

    def get_all_latest(self):
        latest_date_query = f"""SELECT MAX(data) FROM {self.table_name}"""
        latest_date = self.mysql_obj.execute_read_query(latest_date_query)
        if latest_date:
            query = f"""
            SELECT
                fechamento_ajustado, data, id_investimento
            FROM
                {self.table_name}
            WHERE
                {self.table_name}.data = '{latest_date[0][0]}'
            """
            return self.mysql_obj.execute_read_query(query)
        return None

    def get_id(self, date, investment_id):
        query = f"""
        SELECT id FROM {self.table_name}
            WHERE
                {self.table_name}.data = '{date}'
            AND
                {self.table_name}.id_investimento = {investment_id}
        """
        stock_data = self.mysql_obj.execute_read_query(query)
        if stock_data:
            stock_data = stock_data[0][0]
        return stock_data

    def insert(self, **kwargs):
        insert = f"""
            INSERT INTO
                {self.table_name} (
                    abertura, alta,
                    baixa, fechamento,
                    fechamento_ajustado, volume,
                    dividendo, coeficiente_divisao,
                    data, id_investimento
                )
            VALUES (
                {kwargs['open']}, {kwargs['high']},
                {kwargs['low']}, {kwargs['close']},
                {kwargs['adjusted_close']}, {kwargs['volume']},
                {kwargs['dividend_amount']}, {kwargs['split_coefficient']},
                '{kwargs['date']}', {kwargs['investment_id']}
            )
        """
        if not self.get_id(kwargs['date'], kwargs['investment_id']):
            self.mysql_obj.execute_query(insert)

    def insert_multiple(self, stocks_data_frame, investment_id):
        for stock in stocks_data_frame.itertuples():
            stock_kwargs = {
                'open': stock.open, 'high': stock.high,
                'low': stock.low, 'close': stock.close,
                'adjusted_close': stock.adjusted_close, 'volume': stock.volume,
                'dividend_amount': stock.dividend_amount, 'split_coefficient': stock.split_coefficient,
                'date': stock[0], 'investment_id': investment_id
            }
            self.insert(**stock_kwargs)
