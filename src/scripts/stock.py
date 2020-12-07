import random
import time

from alpha_vantage.timeseries import TimeSeries
import pandas as pd

from constants import INVESTMENT_TYPE, TICKERS
from models.investment import Investment
from models.investment_type import InvestmentType
from models.stock import Stock


class StockImport:
    df = pd.DataFrame()

    def __init__(self, mysql_obj, api_key, full_import):
        self.mysql_obj = mysql_obj
        self.api_key = api_key
        self.investment = {
            'name': '',
            'symbol': ''
        }
        self.full_import = full_import

    def run(self):
        five_api_calls_per_minute = 60 / 5

        self.insert_investment_type()

        if self.full_import:
            tickers = TICKERS.items()
        else:
            tickers = [random.choice(list(TICKERS.items())) for i in range(10)]

        for investment_symbol, investment_name in tickers:
            self.investment['name'] = investment_name
            self.investment['symbol'] = investment_symbol
            self.create_df()
            self.insert_investment()
            self.insert_stocks()
            time.sleep(five_api_calls_per_minute)

    def create_df(self):
        ts = TimeSeries(self.api_key)
        if self.full_import:
            data, meta_data = ts.get_daily_adjusted(symbol=self.investment['symbol'], outputsize='full')
        else:
            data, meta_data = ts.get_daily_adjusted(symbol=self.investment['symbol'], outputsize='compact')
        data_df = pd.DataFrame(data)
        data_df = data_df.T
        data_df.columns = [
            'open', 'high',
            'low', 'close',
            'adjusted_close', 'volume',
            'dividend_amount', 'split_coefficient'
        ]
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
        investment.insert(self.investment['name'], investment_type_id)

    def insert_stocks(self):
        investment = Investment(self.mysql_obj)
        investment_id = investment.get_id(self.investment['name'])
        stock = Stock(self.mysql_obj)
        stock.insert_multiple(self.df, investment_id)
