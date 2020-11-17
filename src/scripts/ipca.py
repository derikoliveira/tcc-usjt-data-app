from bs4 import BeautifulSoup

from models.variable_income import VariableIncome
from models.variable_income_type import VariableIncomeType
from selenium_connector import SeleniumConnector
from utils import format_float

URL = 'https://www.ibge.gov.br/explica/inflacao.php'


class IPCAImport:
    soup = None
    ipca_html = ''
    ipca_value = ''

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def run(self):
        self.search_data()
        self.find_data_in_html()
        self.parse_data()
        self.insert_data()

    def search_data(self):
        print('Searching data')
        selenium = SeleniumConnector(URL, options=['--headless', '--no-sandbox'])
        html = selenium.get_html()
        self.soup = BeautifulSoup(html, 'html.parser')

    def find_data_in_html(self):
        print('Parsing data')
        ul = self.soup.find('ul', id='dadoBrasil')
        if not ul:
            raise ValueError('Não foi possível buscar os dados do IPCA, tente novamente')
        ipca = ul.find('p', class_='variavel-dado')
        self.ipca_html = ipca

    def parse_data(self):
        self.ipca_value = format_float(self.ipca_html.text)

    def insert_data(self):
        name = 'IPCA'
        variable_income_type = VariableIncomeType(self.mysql_obj)
        variable_income = VariableIncome(self.mysql_obj)

        variable_income_type.insert(name)
        variable_income_type_id = variable_income_type.get_id(name)

        variable_income.insert(self.ipca_value, variable_income_type_id)
