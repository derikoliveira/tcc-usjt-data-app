from constants import TABLE_NAMES


class DimTime:
    table_name = TABLE_NAMES['dim_time']

    def __init__(self, mysql_obj):
        self.mysql_obj = mysql_obj

    def get_id(self, date):
        query = f"""SELECT id FROM {self.table_name} WHERE {self.table_name}.data = '{date}'"""
        dim_time = self.mysql_obj.execute_read_query(query)
        if dim_time:
            dim_time_id = dim_time[0][0]
            return dim_time_id
        return None

    def insert(self, date):
        if not self.get_id(date):
            insert = f"""INSERT INTO {self.table_name} (data) VALUES ('{date}')"""
            self.mysql_obj.execute_query(insert)

    def insert_multiple(self, dates):
        for date in dates:
            self.insert(date)
