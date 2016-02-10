from database import Database
from server import Server
import json
import os


class Instance:
    def __init__(self, secrets_location):
        if os.path.isfile(secrets_location) and os.access(secrets_location, os.R_OK):
            j = json.loads(open(secrets_location).read())
            self.database = Database(j['database']['host'],j['database']['port'],j['database']['username'],j['database']['password'],j['database']['dbname'])
            self.server = Server(j['dhis']['baseurl'],j['dhis']['username'],j['dhis']['password'])
