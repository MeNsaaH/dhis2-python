from dhis.config import Config
from dhis.server import Server
from dhis.types import *

api=Server()
#api=Server(Config(config_file))
#api=Server(Config(config_url))
#api=Server(Config({..}))

api.get("dataElements")

api.get("dataElements",return_type="request")
api.get("dataElements",return_type="json")
api.get("dataElements",return_type="collection")

api.get("dataElements",fields="id,name",return_type="collection")
api.get("dataElements",filter=["type:eq:int"],return_type="collection")
api.get("dataElements",fields="id,name"","filter=["type:eq:int"],return_type="collection")

## Proposed API declaration 
## api.define("dataElements",return_type="collection",params=['fields','filter'],types={'fields': fieldlist,'filter': filter_string})
