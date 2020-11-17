from argparse import ArgumentParser

from scripts.cdi import CDIImport
from scripts.fact_stock import FactStockImport
from scripts.ipca import IPCAImport
from scripts.prediction import PredictionImport
from scripts.selic import SELICImport
from scripts.stock import StockImport
from scripts.forex import ForexImport
from scripts.tesouro_direto import TesouroDiretoImport
from scripts.suggestion import SuggestionImport
from setup import setup


def main():
    full_import = args()
    mysql_obj, api_key, api_key_hgbrasil = setup()

    IPCAImport(mysql_obj).run()
    SELICImport(mysql_obj, api_key_hgbrasil).run()
    CDIImport(mysql_obj, api_key_hgbrasil).run()
    TesouroDiretoImport(mysql_obj).run()
    ForexImport(mysql_obj, api_key).run()
    StockImport(mysql_obj, api_key, full_import).run()

    FactStockImport(mysql_obj).run()

    PredictionImport(mysql_obj).run()

    SuggestionImport(mysql_obj).run()

    mysql_obj.connection.close()
    print('Data imported successfully!')


def args():
    parser = ArgumentParser()
    parser.add_argument('-f', '--full', action='store_true', default=False, help='Full import')
    args = parser.parse_args()
    return args.full


if __name__ == '__main__':
    main()
