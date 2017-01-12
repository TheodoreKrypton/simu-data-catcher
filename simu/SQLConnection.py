import MySQLdb


class Connection:
    def __init__(self):
        self.conn = MySQLdb.connect(host="localhost", db="fund", user="root", passwd="root", charset="utf8")
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def execute(self, sql):
        self.cursor.execute(sql)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
