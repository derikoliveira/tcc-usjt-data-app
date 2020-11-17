import numpy as np
import pandas as pd

from models.dim_time import DimTime
from models.fact_stock import FactStock
from models.investment import Investment
from models.stock import Stock
from utils import get_past_latest_week_day


class FactStockImport:
    df = None

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def run(self):
        self.create_df()
        self.insert_dim_time()
        self.add_date_id_to_df()
        self.add_past_values_to_df()
        self.add_growth()
        self.insert_fact_stock()

    def create_df(self):
        stock = Stock(self.mysql_obj)
        investment = Investment(self.mysql_obj)
        stocks = stock.get_all_latest()
        columns = ('adjusted_close', 'date', 'investment_id')
        df = pd.DataFrame(stocks, columns=columns)
        investments_ids = tuple(df['investment_id'].unique())
        investments = investment.get_all_by_ids(investments_ids)
        for inv in investments:
            df.loc[df['investment_id'] == inv[0], 'investment_name'] = inv[1]
        self.df = df

    def insert_dim_time(self):
        dim_time = DimTime(self.mysql_obj)
        dates = self.df['date']
        dim_time.insert_multiple(dates)

    def add_date_id_to_df(self):
        dim_time = DimTime(self.mysql_obj)
        date = self.df['date'].unique()[0]
        dim_time_id = dim_time.get_id(date)
        self.df['dim_time_id'] = dim_time_id

    def add_past_values_to_df(self):
        latest_date = self.df['date'].unique()[0]
        past_date = get_past_latest_week_day(latest_date)
        stock = Stock(self.mysql_obj)
        stocks = stock.get_close_adjusted_and_investment_id(past_date)
        for s in stocks:
            self.df.loc[self.df['investment_id'] == s[1], 'past_date'] = past_date
            self.df.loc[self.df['investment_id'] == s[1], 'past_adjusted_close'] = s[0]

    def add_growth(self):
        self.df['growth'] = self.df['past_adjusted_close'] - self.df['adjusted_close']
        percentage = np.divide(self.df['past_adjusted_close'], self.df['adjusted_close'])
        self.df['growth_percentage'] = 1 - percentage

    def insert_fact_stock(self):
        fact_stock = FactStock(self.mysql_obj)
        fact_stock.insert_multiple(self.df)
