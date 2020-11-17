from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from constants import INVESTMENT_TYPE
from models.investment import Investment
from models.predicao import Prediction
from models.stock import Stock


class PredictionImport:
    stocks = pd.DataFrame()
    prediction = pd.DataFrame()
    X = np.array([])
    Y = np.array([])
    x_train = np.array([])
    y_train = np.array([])
    x_valid = np.array([])
    y_valid = np.array([])
    model = LinearRegression()

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj
        self.investments_ids = self.get_investment_ids()

    def run(self):
        for investment_id in self.investments_ids:
            if investment_id:
                self.load_df(investment_id[0])
                if not self.stocks.empty:
                    self.train()
                    self.predict()
                    self.save_prediction(investment_id[0])

    def get_investment_ids(self):
        investment = Investment(self.mysql_obj)
        investments_ids = investment.get_all_by_investment_type_id(INVESTMENT_TYPE['variable_income_id'])
        return list(investments_ids)

    def load_df(self, investment_id):
        stock = Stock(self.mysql_obj)
        stock_data = stock.get_all_by_investment_id(investment_id)
        if stock_data and len(stock_data) > 60:
            df = pd.DataFrame(stock_data)
            df.columns = ['high', 'low', 'adjusted_close', 'date']
            df.set_index('date', inplace=True)
            df.dropna()
            self.stocks = df.sort_index(ascending=True)

    def train(self):
        self.add_moving_average()
        self.split_training()
        self.linear_regression()

    def add_moving_average(self):
        self.stocks = self.stocks.drop(['low', 'high'], axis=1)
        self.stocks['moving_average_30'] = self.stocks.adjusted_close.rolling(window=30).mean()
        self.stocks['moving_average_7'] = self.stocks.adjusted_close.rolling(window=7).mean()
        # Removing stocks without moving average
        self.stocks = self.stocks[29:]

    def split_training(self):
        stocks_split = int(len(self.stocks) * 0.7)

        train = self.stocks[:stocks_split]
        valid = self.stocks[stocks_split:]

        self.x_train = train.drop('adjusted_close', axis=1)
        self.y_train = train['adjusted_close']
        self.x_valid = valid.drop('adjusted_close', axis=1)
        self.y_valid = valid['adjusted_close']

    def linear_regression(self):
        self.model.fit(self.x_train, self.y_train)
        # make predictions and find the rmse
        preds = self.model.predict(self.x_valid)
        rms = np.sqrt(np.mean(np.power((np.array(self.y_valid) - np.array(preds)), 2)))
        print(rms)

    def predict(self):
        self.generate_nan_rows()
        pred = self.prediction
        one_day = np.timedelta64(1, 'D')
        seven_days = np.timedelta64(7, 'D')
        thirty_days = np.timedelta64(30, 'D')
        count = 0
        for i, stock_data in pred.iterrows():
            if np.isnan(stock_data.adjusted_close):
                pred.loc[i].moving_average_7 = pred.iloc[count - 7:count - 1].moving_average_7.mean()
                pred.loc[i].moving_average_30 = pred.iloc[count - 29:count - 1].moving_average_30.mean()
                # predict
                pred.loc[i].adjusted_close = self.model.predict([pred.loc[i].drop('adjusted_close')])
            count += 1

    def generate_nan_rows(self):
        num_days = 30
        current_day = self.stocks.iloc[-1].name
        num_days_td = np.timedelta64(num_days, 'D')
        self.prediction = self.stocks[-30:].copy()
        prediction_future = pd.DataFrame()
        prediction_future['day'] = pd.date_range(current_day, current_day + num_days_td, freq='B')
        prediction_future.set_index(['day'], inplace=True)
        series_nan = pd.Series({'adjusted_close': np.nan, 'moving_average_30': np.nan, 'moving_average_7': np.nan})
        for index, values in prediction_future.iterrows():
            self.prediction.loc[index] = series_nan

    def save_prediction(self, investment_id):
        prediction = self.prediction.loc[pd.to_datetime(datetime.today().date()):]
        Prediction(self.mysql_obj).insert_multiple(prediction, investment_id)
        self.stocks = pd.DataFrame()
