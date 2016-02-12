import base64,  requests
from dhis.config import Config
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
            baseurl=urlunparse(baseurl)
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
        return base64.encodebytes('%s:%s' % (self.username, self.password)).replace('\n', '')

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

    wrapper_params=['return_type','content-type','content-length',
                    'content-encoding','date','host','auth']

    def call(self,endpoint,method=None,return_type=None,params={},headers={},**kwargs):
        auth=self.credentials
        nkwargs=self.__sec(headers)
        baseurl=self.baseurl
        if type(endpoint) is str:
            if action.endsWith('json') and not return_type:
                use_return_type='json'
            elif not return_type:
                use_return_type='request'
            else:
                use_return_type=return_type
            endpoint=Endpoint({'name': endpoint,'relpath': endpoint,
                               'method': method,params: None,
                               'return_type': use_return_type})
        if not method and endpoint.method:
            method=endpoint.method
        elif not method:
            method="GET"
        path=baseurl+endpoint.relpath
        if not return_type:
            return_type=endpoint.return_type
        if endpoint.params:
            for arg in endpoint.params:
                params[arg]=kwargs.get(arg)
        else:
            for item in kwargs.items():
                if item[0] not in Server.wrapper_params:
                    params[item[0]]=item[1]
        if method == 'GET':
            result=requests.get(path,params=params,**nkwargs)
        elif method == 'PUT':
            result=requests.put(path,params=params,**nkwargs)
        elif method == 'POST':
            result=requests.post(path,params=params,**nkwargs)
        elif method == 'PATCH':
            result=requests.patch(path,params=params,**nkwargs)
        elif method == 'DELETE':
            result=requests.delete(path,params=params,**nkwargs)
        else:
            result=requests.get(path,params=params,**nkwargs)
        result=self.__out(result)
        if return_type == 'request':
            return result
        elif result.status_code != 200:
            raise Exception('HTTP error',result)
        elif not endpoint.return_type:
            return result
        elif endpoint.return_type == 'json':
            return result.json()
        elif endpoint.return_type == 'text':
            return result.text
        else:
            return result

    def get(self, path, **kwargs):
        return self.call(path,"GET",**kwargs)

    def put(self, path, **kwargs):
        return self.call(path,"PUT",**kwargs)

    def post(self, path, **kwargs):
        return self.call(path,"POST",**kwargs)

    def patch(self, path, **kwargs):
        return self.call(path,"PATCH",**kwargs)

    def delete(self, path, **kwargs):
        return self.call(path,"DELETE",**kwargs)

    def clear_hibernate_cache(self):
        return self._out(requests.get(self.baseurl + "/dhis-web-maintenance-dataadmin/clearCache.action"))

class Endpoint:
    def __init__(self,info,server=None):
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