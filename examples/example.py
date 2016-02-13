from dhis import Secrets
from dhis import Server
from dhis import Database
mysecrets=Secrets('/home/foo/.secrets/local.json')
myserver=Server(mysecrets.dhis())
foo=myserver.get('api/dataElements/')
foo.json()
mydatabase=Database(mysecrets.dsn())
foo="UPDATE dataelement set name = \'bar\' where uid = \'oYuFPjjIlF\'"
mydatabase.execute(foo)
foo="SELECT name from dataelement where uid = \'koYuFPjjIlF\'"
mydatabase.fetchall(foo)
mydatabase.cur.execute(foo)
