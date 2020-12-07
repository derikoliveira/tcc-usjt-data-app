from constants import TABLE_NAMES, USD_BRL_NAME
from models.investment import Investment


class USDBRL:
    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.table_name = TABLE_NAMES['dollar']

    def get_id(self, date, investment_id):
        query = f"""
        SELECT id FROM {self.table_name}
        WHERE
            {self.table_name}.data = '{date}'
        AND
            {self.table_name}.id_investimento = {investment_id}
        """
        usd_brl = self.mysql_obj.execute_read_query(query)
        if usd_brl:
            usd_brl_id = usd_brl[0][0]
            return usd_brl_id
        return None

    def insert(self, **kwargs):
        insert = f"""
            INSERT INTO
                {self.table_name} (abertura, alta, baixa, fechamento, data, id_investimento)
            VALUES (
                {kwargs['open']}, {kwargs['high']},
                {kwargs['low']}, {kwargs['close']},
                '{kwargs['date']}', {kwargs['investment_id']}
            )
        """
        if not self.get_id(kwargs['date'], kwargs['investment_id']):
            self.mysql_obj.execute_query(insert)

    def insert_multiple(self, usd_brl_data_frame):
        investment = Investment(self.mysql_obj)
        investment_id = investment.get_id(USD_BRL_NAME)
        for usd_brl in usd_brl_data_frame.itertuples():
            usd_brl_kwargs = {
                'open': usd_brl.open, 'high': usd_brl.high,
                'low': usd_brl.low, 'close': usd_brl.close,
                'date': usd_brl[0], 'investment_id': investment_id,
            }
            self.insert(**usd_brl_kwargs)
