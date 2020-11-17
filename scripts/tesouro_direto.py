import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime

from constants import INVESTMENT_TYPE
from models.fixed_income import FixedIncome
from models.variable_income import VariableIncome
from models.variable_income_type import VariableIncomeType
from models.investment import Investment
from models.investment_type import InvestmentType
from selenium_connector import SeleniumConnector
from utils import format_float

URL = 'https://www.tesourodireto.com.br/titulos/precos-e-taxas.htm'

TITULO_PUBLICO_KEYS = {
    'invest': (
        'title', 'annual_profitability',
        'minimum_investment', 'unit_price',
        'due_date',
    ),
    'redeem': (
        'title', 'annual_profitability',
        'unit_price', 'due_date'
    )
}


class TesouroDiretoImport:
    titulos_publicos = {
        'invest': [],
        'redeem': [],
    }
    titulo_publico = {'type': ''}
    titulos_publicos_dfs = {
        'investment': pd.DataFrame(),
        'redeem': pd.DataFrame(),
    }
    soup = None

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def run(self):
        print('Importing Tesouro Direto')
        self.search_data()
        self.parse_data()
        self.import_data()

    def search_data(self):
        print('Searching data')
        selenium = SeleniumConnector(URL, options=['--headless', '--no-sandbox'])
        html = selenium.get_html()
        self.soup = BeautifulSoup(html, 'html.parser')

    def parse_data(self):
        print('Parsing data')
        tables = self.soup.find_all('table')
        if not tables:
            raise ValueError('Não foi possível buscar os dados do Tesouro Direto, tente novamente')
        invest = tables[0]
        redeem = tables[1]
        self.titulo_publico['type'] = 'invest'
        self.get_table_data(invest)
        self.titulo_publico['type'] = 'redeem'
        self.get_table_data(redeem)

    def get_table_data(self, table):
        """
        HTML Invest Table:
        Título                       | Rentabilidade anual | Investimento mínimo | Preço Unitário | Vencimento
        TESOURO PREFIXADO 2023 Ajuda | 4,56%               | R$ 35,61            | R$ 890,40      | 01/01/2023 | Simule

        HTML Redeem Table:
        Título                 | Rentabilidade anual | Preço Unitário | Vencimento
        TESOURO PREFIXADO 2021 | 2,57%               | R$ 984,61      | 01/01/2021
        """
        rows = table.find_all('tr', class_='td-invest-table__row')
        tp_type = self.titulo_publico['type']
        for row in rows:
            titulo_publico = self.parse_row(row)
            if titulo_publico:
                self.titulos_publicos[tp_type].append(titulo_publico)

    def parse_row(self, row):
        row_parsed = []
        cols = row.find_all('td')
        for col_index, col in enumerate(cols):
            col_function = self.get_col_function(col_index)
            if col_function:
                col_parsed = col_function(col)
                row_parsed.append(col_parsed)
        return row_parsed

    def get_col_function(self, col_index):
        switcher = {
            'invest': {
                0: self.get_title,
                1: self.get_annual_profitability,
                2: self.get_minimum_investment,
                3: self.get_unit_price,
                4: self.get_due_date,
            },
            'redeem': {
                0: self.get_title,
                1: self.get_annual_profitability,
                2: self.get_unit_price,
                3: self.get_due_date,
            }

        }
        tp_type = self.titulo_publico['type']
        return switcher[tp_type].get(col_index)

    @staticmethod
    def get_title(col):
        return col.find_all('span')[0].text.replace('\t', '').strip()

    @staticmethod
    def get_annual_profitability(col):
        """
        HTML Col Types:
            1. 7,57%
            2. SELIC + 0,03%
            3. IPCA + 3,08%
        """
        col = col.find('span').text.lower()
        col_clean = col.replace('selic', '').replace('ipca', '').replace('+', '')
        col_clean = format_float(col_clean)

        if 'selic' in col:
            annual_profitability = (col_clean, 'SELIC')
        elif 'ipca' in col:
            annual_profitability = (col_clean, 'IPCA')
        else:
            annual_profitability = (col_clean,)
        return annual_profitability

    @staticmethod
    def get_minimum_investment(col):
        minimum_investment = format_float(col.find('span').text)
        return minimum_investment

    @staticmethod
    def get_unit_price(col):
        unit_price = format_float(col.find('span').text)
        return unit_price

    @staticmethod
    def get_due_date(col):
        col_clean = col.find('span').text.strip()
        due_date = datetime.strptime(col_clean, '%d/%m/%Y')
        return due_date

    def import_data(self):
        print('Importing data')
        columns_invest = TITULO_PUBLICO_KEYS['invest']
        columns_redeem = TITULO_PUBLICO_KEYS['redeem']

        invest_df = pd.DataFrame(self.titulos_publicos['invest'], columns=columns_invest)
        redeem_df = pd.DataFrame(self.titulos_publicos['redeem'], columns=columns_redeem)

        self.titulos_publicos_dfs['invest'] = invest_df
        self.titulos_publicos_dfs['redeem'] = redeem_df

        self.insert_investment_type()
        self.insert_investment()
        self.insert_fixed_income()

    def insert_investment_type(self):
        name = INVESTMENT_TYPE['fixed_income']
        investment_type = InvestmentType(self.mysql_obj)
        investment_type.insert(name)

    def insert_investment(self):
        investment_type = InvestmentType(self.mysql_obj)
        investment_type_id = investment_type.get_id(INVESTMENT_TYPE['fixed_income'])
        investment = Investment(self.mysql_obj)

        invest_df = self.titulos_publicos_dfs['invest']['title']
        redeem_df = self.titulos_publicos_dfs['redeem']['title']

        for titulo_publico_name in invest_df:
            investment.insert(titulo_publico_name, investment_type_id)

        for titulo_publico_name in redeem_df:
            investment.insert(titulo_publico_name, investment_type_id)

    def insert_income_variable_type(self):
        variable_income_type = VariableIncomeType(self.mysql_obj)
        annual_profitability_invest = self.titulos_publicos_dfs['invest']['annual_profitability']
        annual_profitability_redeem = self.titulos_publicos_dfs['redeem']['annual_profitability']

        variable_income_type.insert_multiple(annual_profitability_invest)
        variable_income_type.insert_multiple(annual_profitability_redeem)

    def insert_income_variable(self):
        variable_income = VariableIncome(self.mysql_obj)
        invest_df = self.titulos_publicos_dfs['invest']
        redeem_df = self.titulos_publicos_dfs['redeem']

        variable_income.insert_multiple(invest_df)
        variable_income.insert_multiple(redeem_df)

    def insert_fixed_income(self):
        fixed_income = FixedIncome(self.mysql_obj)
        invest_df = self.titulos_publicos_dfs['invest']
        redeem_df = self.titulos_publicos_dfs['redeem']
        fixed_income.insert_multiple(invest_df)
        fixed_income.insert_multiple(redeem_df)
