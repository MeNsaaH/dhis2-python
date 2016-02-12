import json, os, urllib
from urllib.parse import urlparse
from urllib.request import urlopen

class Config:
    def __init__(self, location=None,profile=None,isurl=False):
        if not location:
            location=os.getenv('DHIS2_CONFIG')
        elif (os.path.isfile(location)) and os.access(location,os.R_OK):
            location=location
        elif urlparse(location).hostname:
            location=location
            isurl=True
        if location:
            raise Exception('Bad config location',location)
        elif ((os.path.isfile("dhis2conf.json")) and os.access("dhis2conf.json",os.R_OK)):
            location="dhis2conf.json"
        elif (os.path.isfile("~/.dhis2conf.json")) and os.access("~/.dhis2conf.json",os.R_OK):
            location="~/.dhis2conf.json"
        else:
            location=None
        if location:
            print('Loading config from '+os.path.realpath(location),end='\n',flush=True)
        else:
            print('No configuration file',end='\n',flush=True)
        if location:
            if isurl:
                loaded=json.loads(urlopen(location).read())
            else:
                loaded=json.loads(open(location).read())
            if loaded.get('api') or loaded.get('database') or loaded.get('dhis'):
                for item in loaded.items():
                    if type(item[1]) is not str:
                        loaded[item[0]]=Configuration(item[1])
                config=loaded
            elif loaded.get('dbname'):
                config={'database': Configuration(loaded)}
            elif loaded.get('baseurl'):
                config={'api': Configuration(loaded)}
            else:
                raise Exception('odd config',loaded)
        else:
            dbconfig={}
            apiconfig={}
            dbconfig['host']=os.getenv("DHIS2DB_HOST")
            dbconfig['port']=os.getenv("DHIS2DB_PORT")
            dbconfig['username']=os.getenv("DHIS2DB_USER")
            dbconfig['password']=os.getenv("DHIS2DB_PASSWORD")
            dbconfig['database']=os.getenv("DHIS2DB_DBNAME")
            apiconfig['baseurl']=os.getenv("DHIS2API_ROOT")
            apiconfig['username']=os.getenv("DHIS2API_USER")
            apiconfig['password']=os.getenv("DHIS2API_PASSWORD")
            config={'database': Configuration(dbconfig),
                    'api': Configuration(apiconfig)}

        self.config=config
        self.profile=profile
        self.location=location

    def resolve_config(self,config,base):
        probe=base
        while (probe and (type(probe) is str)):
            probe=config.get(probe)
        if probe:
            return probe
        else:
            return config

    def getconfig(self,url=None):
        config=self.config
        if url:
            parsed=urlparse(url)
            probe=url
            if (config.get(probe)):
                return self.resolve_config(config,probe)
            if parsed.port:
                probe='%s:%d'%(parsed.hostname,parsed.port)
            else:
                probe='%s:80'%parsed.hostname
            if (config.get(probe)):
                return self.resolve_config(config,probe)
            probe=parsed.hostname
            if (config.get(probe)):
                return self.resolve_config(config,probe)
            elif self.profile and config.get(self.profile):
                return self.resolve_config(config,self.profile)
            elif (parsed.scheme == 'http' or parsed.scheme == 'https'):
                if (config.get('api')):
                    return self.resolve_config(config,'api')
                else:
                    return config
            else:
                return config
        elif self.profile and config.get(self.profile):
            return self.resolve_config(config,self.profile)
        elif (config.get('db')):
            return self.resolve_config(config,'db')
        elif (config.get('api')):
            return self.resolve_config(config,'api')
        elif (config.get('dhis')):
            return self.resolve_config(config,'dhis')
        else:
            return config
    
class Configuration:
    def __init__(self,configdata):
        self.name=None
        self.configdata=configdata
        self.username=''
        self.password=''
        if configdata.get('baseurl'):
            self.kind='API'
        elif configdata.get('dbname'):
            self.kind='Database'
        else:
            self.kind=None
        if self.kind == "Database":
            self.port=None
            self.hostname='localhost'
        if self.kind == 'API':
            self.baseurl=None
        for item in configdata.items():
            setattr(self,item[0],item[1])

    def __repr__(self):
        if self.kind and self.name:
            return '<%s configuration %s>'%(self.kind,self.name)
        elif self.name:
            return '<Configuration %s>'%self.name
        elif (self.kind == 'API'):
            return '<API configuration for %s@%s>'%(self.username,self.baseurl)
        elif (self.kind == 'Database'):
            return '<DB configuration for %s@%s:%s as %s>'%(self.dbname,self.hostname,self.port,self.username)
        elif (self.kind):
            return '<%s configuration %s>'%(self.kind,str(self.configdata))
        else:
            return '<Configuration '+str(self.configdata)+'>'
        
    def __str__(self):
        if self.kind:
            return '<%s configuration %s>'%(self.kind,str(self.configdata))
        else:
            return '<Configuration %s>'%str(self.configdata)
