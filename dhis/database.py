import psycopg2


class Database:
    def __init__(self, dsn):
        self.dsn = dsn
        try:
            self.conn = psycopg2.connect(dsn)
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError as e:
            print('Could not get a database connection' + e)
        assert isinstance(self.conn, psycopg2.extensions.connection)
        assert isinstance(self.cur, psycopg2.extensions.cursor)

    def __del__(self):
        self.conn.close()

    def execute(self,sql):
        assert (sql, str)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            return e
        else:
            return True

    def fetchall(self,sql):
        assert (sql, str)
        try:
            self.cur.execute(sql)
            return self.cur.fetchall()
        except psycopg2.Error as e:
            return e