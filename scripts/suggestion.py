class SuggestionImport:
    by_growth_query = """
        INSERT INTO TB_SUGESTAO (ID, DATA, VALOR, ID_INVESTIMENTO, ID_TIPO_SUGESTAO)
        SELECT
            NULL
            ,NOW()
            ,(A.FECHAMENTO - F.FECHAMENTO) CRESCIMENTO
            ,A.ID_INVESTIMENTO
            ,2
        FROM
        (
        SELECT
            ID_INVESTIMENTO,
            FECHAMENTO
        FROM 
            TB_ACAO
        GROUP BY
            ID_INVESTIMENTO
        HAVING
            MAX(DATA)
        ) F
        INNER JOIN 
        (
        SELECT
            ID_INVESTIMENTO,
            FECHAMENTO
        FROM 
            TB_ACAO
        GROUP BY
            ID_INVESTIMENTO
        HAVING
            MIN(DATA)
        ) A
        ON F.ID_INVESTIMENTO = A.ID_INVESTIMENTO
        ORDER BY 
            CRESCIMENTO DESC
    """

    by_regularity_query = """
        INSERT INTO TB_SUGESTAO (ID, DATA, VALOR, ID_INVESTIMENTO, ID_TIPO_SUGESTAO)
        SELECT
            NULL,
            NOW(),
            IF((A.ABERTURA - M.MEDIA) < 0, (A.ABERTURA - M.MEDIA) * -1, (A.ABERTURA - M.MEDIA)) AS DIFERENCA,
            A.ID_INVESTIMENTO,
            1
        FROM
        (
        SELECT
            ID_INVESTIMENTO,
            AVG(FECHAMENTO) AS MEDIA
        FROM 
            TB_ACAO
        GROUP BY
            ID_INVESTIMENTO
        ) M
        INNER JOIN 
        (
        SELECT
            ID_INVESTIMENTO,
            ABERTURA
        FROM 
            TB_ACAO
        GROUP BY
            ID_INVESTIMENTO
        HAVING
            MIN(DATA)
        ) A
        ON M.ID_INVESTIMENTO = A.ID_INVESTIMENTO
        ORDER BY 
            DIFERENCA;
    """

    count_suggestion = "SELECT COUNT(*) FROM TB_TIPO_SUGESTAO;"

    insert_suggestion = "INSERT INTO TB_TIPO_SUGESTAO VALUES (NULL, 'Regularidade'), (NULL, 'Cresimento');"

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def run(self):
        count = self.mysql_obj.execute_read_query(self.count_suggestion)

        if int(count[0][0]) == 0:
            self.mysql_obj.execute_query(self.insert_suggestion)

        self.mysql_obj.execute_query(self.by_growth_query)
        self.mysql_obj.execute_query(self.by_regularity_query)
