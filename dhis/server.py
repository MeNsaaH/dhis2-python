import requests

class Server:
    def __init__(self,obj):
        self.baseurl = obj['baseurl']
        self.credentials = (obj['username'], obj['password'])
        self.__cookies = None
    def __sec(self, headers): #Add security, either username/password or cookie
        if  self.__cookies:
            headers["cookies"] = self.__cookies
        else:
            headers["auth"] = self.credentials
        return headers
    def __out(self, result): #First time: Grab seurity cookie for future calls
        if not self.__cookies :
            self.__cookies = {"JSESSIONID": result.cookies["JSESSIONID"]};
        return result

    def get(self, path, **kwargs):
        return self.__out(requests.get(self.baseurl + path, **self.__sec(kwargs)))

    def put(self, path, **kwargs):
        return self.__out(requests.put(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def post(self, path, **kwargs):
        return self.__out(requests.post(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def patch(self, path, **kwargs):
        return self.__out(requests.patch(self.baseurl + path, auth=self.credentials, **self.__sec(kwargs)))

    def clear_hibernate_cache(self):
        return self._out(requests.get(self.baseurl + "/api/maintenance/cache"))

