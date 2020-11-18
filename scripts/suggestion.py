class SuggestionImport:
    max_query = """SELECT 
                            A.ID_INVESTIMENTO, 
                            A.FECHAMENTO 
                        FROM TB_ACAO A 
                            INNER JOIN (
                                SELECT
                                    ID_INVESTIMENTO,
                                    MAX(DATA) AS DATA
                                FROM 
                                    TB_ACAO
                                GROUP BY
                                    ID_INVESTIMENTO) B 
                            ON A.ID_INVESTIMENTO = B.ID_INVESTIMENTO AND A.DATA = B.DATA"""

    min_query = """SELECT 
                        A.ID_INVESTIMENTO, 
                        A.FECHAMENTO 
                    FROM TB_ACAO A 
                        INNER JOIN (
                            SELECT
                                ID_INVESTIMENTO,
                                MIN(DATA) AS DATA
                            FROM 
                                TB_ACAO
                            GROUP BY
                                ID_INVESTIMENTO) B 
                        ON A.ID_INVESTIMENTO = B.ID_INVESTIMENTO AND A.DATA = B.DATA"""

    avg_query = """SELECT
                        ID_INVESTIMENTO,
                        AVG(FECHAMENTO) AS MEDIA
                    FROM 
                        TB_ACAO
                    GROUP BY
                        ID_INVESTIMENTO"""
    
    fixed_income_query = """SELECT 
                                A.ID_INVESTIMENTO, 
                                A.RENDIMENTO_FIXO 
                            FROM TB_RENDA_FIXA A 
                                INNER JOIN (
                                    SELECT
                                        ID_INVESTIMENTO,
                                        MIN(DATA) AS DATA
                                    FROM 
                                        TB_RENDA_FIXA
                                    GROUP BY
                                        ID_INVESTIMENTO) B 
                                ON A.ID_INVESTIMENTO = B.ID_INVESTIMENTO AND A.DATA = B.DATA"""
    
    count_suggestion = "SELECT COUNT(*) FROM TB_TIPO_SUGESTAO;"

    insert_suggestion = "INSERT INTO TB_TIPO_SUGESTAO VALUES (NULL, 'Regularidade'), (NULL, 'Cresimento'), (NULL, 'Perfil');"

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def run(self):
        count = self.mysql_obj.execute_read_query(self.count_suggestion)

        if int(count[0][0]) == 0:
            self.mysql_obj.execute_query(self.insert_suggestion)

        by_regularity = self.calculate(self.min_query, self.avg_query, lambda a, b : (a - b) < 0 if (a - b) * -1 else a - b)
        self.insert(by_regularity, 1)

        by_growth = self.calculate(self.min_query, self.max_query, lambda a, b : a - b)
        self.insert(by_growth, 2)
        self.insert(by_growth, 3)

        by_fixed_income = self.mysql_obj.execute_read_query(self.fixed_income_query)
        self.insert(by_fixed_income, 3)
        
    def insert(self, tuple, id_tipo_sugestao):
        for i in range(len(tuple)):
            query = f"INSERT INTO TB_SUGESTAO (ID, DATA, VALOR, ID_INVESTIMENTO, ID_TIPO_SUGESTAO) VALUES (NULL, NOW(), {tuple[i][1]}, {tuple[i][0]}, {id_tipo_sugestao})"
            self.mysql_obj.execute_query(query)

    def calculate(self, query_one, query_two, func):
        result_query_one = self.mysql_obj.execute_read_query(query_one)
        result_query_two = self.mysql_obj.execute_read_query(query_two)

        inner = self.inner_join(result_query_one, result_query_two, func)

        return inner
    
    def inner_join(self, a, b, func):
        inner = []

        for i in range(len(a)):
            for j in range(len(b)):
                if a[i][0] == b[j][0]:
                    result = func(a[i][1], b[j][1])
                    inner.append((a[i][0], result))
        
        return inner