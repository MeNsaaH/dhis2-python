import base64, config, urllib, requests
from config import Config
from urllib.parse import urlparse, urlunparse

class Server:
    def __init__(self, baseurl=None, config=None, username=None, password=None,profile=None):
        config=Config(config,profile=profile)
        if not baseurl:
            baseurl=config.getconfig("api").baseurl
        if not baseurl:
            raise Exception('Server requires baseurl')
        elif type(baseurl) is not str:
            # Handle unparsed URLs as baseurls
            baseurl=unparseurl(baseurl)
        if not urlparse(baseurl).hostname:
            raise Exception('Bad baseurl arg',baseurl)
        if baseurl.endswith('/api/'):
            baseurl=baseurl
        elif baseurl.endswith('/'):
            baseurl=baseurl+'api/'
        else: 
            baseurl=baseurl+'/api/'
        if not username:
            username=config.getconfig(baseurl).username
        if type(username) is not str:
            raise Exception('bad username',username)
        if not password:
            password=config.getconfig(baseurl).password
        if type(password) is not str:
            # Don't pass the password arg to try and keep it out of
            # error messages which anyone might see
            raise Exception('bad password')
        self.baseurl=baseurl
        self.username=username
        self.password=password
        self.credentials = (username, password)
        self.endpoints={}
        self.__cookies = None

    def get_auth_string(self):
        return base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')

    def __sec(self, headers): #Add security, either username/password or cookie
        if  self.__cookies:
            headers["cookies"] = self.__cookies
        else:
            headers["auth"] = self.credentials
        return headers

    def __out(self, result): #First time: Grab security cookie for future calls
        if not self.__cookies and result.cookies and result.cookies["JSESSIONID"]:
            self.__cookies = {"JSESSIONID": result.cookies["JSESSIONID"]}
        return result

    def get(self, path, **kwargs):
        return self.__out(requests.get(self.baseurl + path, **self.__sec(kwargs)))

    def put(self, path, **kwargs):
        return self.__out(requests.put(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def post(self, path, **kwargs):
        return self.__out(requests.post(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def patch(self, path, **kwargs):
        return self.__out(requests.patch(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def call(self,action,return_type=None, **kwargs):
        info=self.endpoints.get(action)
        if not info:
            if action.endsWith('json') and not return_type:
                use_return_type='json'
            elif not return_type:
                use_return_type='request'
            else:
                use_return_type=return_type
            info={'name': action,'relpath': action,
                  'method': 'get',
                  'return_type': use_return_type,
                  'params': None}
        method=info.method
        params={}
        if not return_type:
            return_type=info.return_type
        if info.params:
            for arg in info.params:
                params[arg]=kwargs.get(arg)
        else:
            for item in kwargs.items():
                params[item[0]]=item[1]
        if method == 'GET':
            result=self.get(info.relpath,params=params)
        elif method == 'PUT':
            result=self.put(info.relpath,params=params)
        elif method == 'POST':
            result=self.put(info.relpath,params=params)
        elif method == 'PATCH':
            result=self.patch(info.relpath,params=params)
        else:
            result=requests.get(inf.relpath,params=params)
        result=self.__out(result)
        if return_type == 'request':
            return result
        elif result.status_code != 200:
            raise Exception('HTTP error',result)
        elif not info.return_type:
            return result
        elif info.return_type == 'json':
            return result.json()
        elif info.return_type == 'text':
            return result.text
        else:
            return result

    def addEndpoint(self,definition):
        if definition.get('name'):
            key=definition.get('name')
        elif definition.get('relpath'):
            key=definition.get('relpath')
        else:
            raise Exception('No name for endpoint')
        endpoint=Endpoint(definition,self)
        self.endpoints[key]=endpoint
        return endpoint

    def clear_hibernate_cache(self):
        return self._out(requests.get(self.baseurl + "/dhis-web-maintenance-dataadmin/clearCache.action"))

class Endpoint:
    def __init__(self,info,server):
        self.name=None
        self.info=info
        self.server=server
        self.method="GET"
        self.params=None
        self.return_type=None
        for item in info.items():
            setattr(self,item[0],item[1])
        if not self.return_type and self.relpath and self.relpath.endswith('json'):
            self.return_type='json'

    def __repr__(self):
        if self.name:
            return '<Endpoint %s>'%self.name
        else:
            return '<Endpoint '+str(self.info)+'>'
        
    def __str__(self):
        if self.name:
            return '<Endpoint %s>'%self.name
        else:
            return '<Endpoint '+str(self.info)+'>'
