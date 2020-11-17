import numpy as np
import pandas as pd


def format_float(text):
    clean_text = text.replace('R$', '').replace('.', '').replace(',', '.').replace('%', '').strip()
    return float(clean_text)


def get_past_latest_week_day(date):
    weekends = [5, 6]  # saturday, sunday
    one_day = np.timedelta64(1, 'D')
    past_date = pd.to_datetime(date - one_day)
    while past_date.weekday() in weekends:
        past_date = pd.to_datetime(past_date - one_day)
    return date
