from mysql_conn import MySQL

try:
    from local_settings import API_KEY, DB_USER, DB_PASSWORD, API_KEY_HGBRASIL, DB_NAME, HOST
except ImportError:
    pass


def setup():
    try:
        mysql_user = DB_USER
    except NameError:
        mysql_user = input('Insert your MySQL username\n')

    try:
        mysql_password = DB_PASSWORD
    except NameError:
        mysql_password = input('Insert your MySQL password\n')

    try:
        db_name = DB_NAME
    except NameError:
        db_name = 'sistema_investimento'

    try:
        host = HOST
    except NameError:
        host = 'localhost'

    mysql_obj = MySQL(host, mysql_user, mysql_password, db_name)

    try:
        api_key = API_KEY
    except NameError:
        api_key = input('Insert your API key\n')

    try:
        api_key_hgbrasil = API_KEY_HGBRASIL
    except NameError:
        api_key_hgbrasil = input('Insert your API HGBrasil key (https://console.hgbrasil.com/keys/new_key_plan)\n')

    return mysql_obj, api_key, api_key_hgbrasil
