from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd

from constants import EXCHANGE_RATE_SYMBOLS, USD_BRL_NAME, INVESTMENT_TYPE
from models.investment import Investment
from models.investment_type import InvestmentType
from models.usd_brl import USDBRL


class ForexImport:
    df = pd.DataFrame()

    def __init__(self, mysql_obj, api_key):
        self.mysql_obj = mysql_obj
        self.api_key = api_key

    def run(self):
        self.create_data_frame()
        self.insert_investment_type()
        self.insert_investment()
        self.insert_usd_brl()

    def create_data_frame(self):
        fe = ForeignExchange(key=self.api_key)
        data, _ = fe.get_currency_exchange_daily(from_symbol=EXCHANGE_RATE_SYMBOLS['from_symbol'],
                                                 to_symbol=EXCHANGE_RATE_SYMBOLS['to_symbol'],
                                                 outputsize='full')
        data_df = pd.DataFrame(data)
        data_df = data_df.T
        data_df.columns = ['open', 'high', 'low', 'close']
        data_df.index = pd.DatetimeIndex(data_df.index)
        self.df = data_df

    def insert_investment_type(self):
        name = INVESTMENT_TYPE['variable_income']
        investment_type = InvestmentType(self.mysql_obj)
        investment_type.insert(name)

    def insert_investment(self):
        investment_type = InvestmentType(self.mysql_obj)
        investment = Investment(self.mysql_obj)
        investment_type_id = investment_type.get_id(INVESTMENT_TYPE['variable_income'])
        investment.insert(USD_BRL_NAME, investment_type_id)

    def insert_usd_brl(self):
        usd_brl = USDBRL(self.mysql_obj)
        usd_brl.insert_multiple(self.df)
