import psycopg2


class Database:
    def __init__(self, host=None, port=None, username=None, password=None, dbname=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname
        try:
            self.conn = psycopg2.connect(self.dsn())
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError as e:
            print('Could not get a database connection' + e)
        assert isinstance(self.conn, psycopg2.extensions.connection)
        assert isinstance(self.cur,psycopg2.extensions.cursor)

    def __del__(self):
        self.conn.close()

    def dsn(self):
        return "dbname=" + self.dbname + \
               " host=" + self.host + \
               " user=" + self.username + \
               " password=" + self.password + \
               " port=" + str(self.port)

    def execute_sql(self,sql):
        try:
            for command in sql:
                self.cur.execute(command)
                self.conn.commit()
        except psycopg2.Error as e:
            print e
            self.conn.rollback()
            return False
        else:
            return True