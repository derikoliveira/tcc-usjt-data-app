import requests

from models.variable_income import VariableIncome
from models.variable_income_type import VariableIncomeType

URL = 'https://api.hgbrasil.com/finance/taxes?key={}'


class CDIImport:
    soup = None
    cdi_html = ''
    cdi_value = 0.0

    def __init__(self, mysql_obj, api_key_hgbrasil):
        self.mysql_obj = mysql_obj
        self.api_key_hgbrasil = api_key_hgbrasil

    def run(self):
        self.get_value()
        self.insert_data()

    def get_value(self):
        response = requests.get(URL.format(self.api_key_hgbrasil))
        self.cdi_value = response.json()['results'][0]['cdi_daily']

    def insert_data(self):
        name = 'CDI'
        variable_income_type = VariableIncomeType(self.mysql_obj)
        variable_income = VariableIncome(self.mysql_obj)

        variable_income_type.insert(name)
        variable_income_type_id = variable_income_type.get_id(name)

        variable_income.insert(self.cdi_value, variable_income_type_id)
