import base64
import json
import model
from com.blakey.network import HttpSession
from com.blakey.exception import InvalidCredentialError, HostIsNotReachableError


class RedfishSession(object):
    ROOT_URL = "/rest/v1"

    def __init__(self, host, username, password, use_basic_auth=True):
        self.host = host
        self.username = username
        self.password = password
        self.http = HttpSession(self.host)
        self.logout_location = None
        self.services = {}
        self.data_model = None
        self.init()
        self.use_basic_auth = use_basic_auth

    def init(self):
        try:
            self.data_model = self.get_root()
        except Exception, e:
            raise HostIsNotReachableError()

    def login(self):
        if self.use_basic_auth:
            self.http.set_extra_header({"Authorization": self.gen_auth_token()})
        else:
            self._login()

    def _login(self):
        data = {"UserName": self.username, "Password": self.password}
        json_data = json.dumps(data)
        resp = self.http.post(self.data_model.links.Sessions.href, json_data)

        if not resp.is_successful():
            raise InvalidCredentialError()
        self.logout_location = resp.get_new_location()
        self.http.set_extra_header(resp.get_session_key())

    def logout(self):
        if self.logout_location is not None:
            resp = self.http.delete(self.logout_location)
            if not resp.is_successful():
                print "Logout:" + str(resp)

    def gen_auth_token(self):
        base64str = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        ret = "Basic %s" % base64str
        return ret

    def get_root(self):
        resp = self.http.get(self.ROOT_URL)
        data_model = model.DataModel.parse(resp.body)
        for key, value in data_model.links:
            # ignore "self" attribute
            if key in ("self",):
                continue
            self.services[key] = value.href
        return data_model

    def get_services_list(self):
        return self.services

    def create(self, url, data):
        return self.http.post(url, data)

    def read(self, url):
        return self.http.get(url)

    def update(self, url, data):
        return self.http.patch(url, data)

    def delete(self, url):
        return self.http.delete(url)

    def get_vendor(self):
        return self.data_model.Name.encode('utf8')


class Session(object):
    pass