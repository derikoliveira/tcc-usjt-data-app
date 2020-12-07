import mysql
from mysql.connector import Error


class MySQL:
    def __init__(self, host_name, user_name, user_password, db_name):
        self.host_name = host_name
        self.user_name = user_name
        self.user_password = user_password
        self.db_name = db_name
        self.connection = self.create_connection()

    def create_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host_name,
                user=self.user_name,
                passwd=self.user_password,
                database=self.db_name
            )
            print("Connection to MySQL DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def execute_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    # executa queries parametrizadas
    def execute_par_query(self, query, pars):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, pars)
            self.connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    def execute_read_query_with_description(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return cursor.description, result
        except Error as e:
            print(f"The error '{e}' occurred")
