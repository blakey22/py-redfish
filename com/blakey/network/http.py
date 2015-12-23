import urllib2
from urllib2 import URLError
import json

class HttpSession(object):
    def __init__(self, host):
        self.host = host
        self.extra_headers = {}

    def send_request(self, http_verb, url, data=None):
        full_url = "https://%s%s" % (self.host, url)
        request = urllib2.Request(full_url, data, self.extra_headers)
        request.get_method = lambda: http_verb
        try:
            resp = urllib2.urlopen(request)
            return HttpResponse(self.host, resp)
        except URLError, e:
            if e is URLError:
                return None
            return HttpResponse(self.host, e)


    def post(self, url, data):
        self.extra_headers["Content-Type"] = "application/json"
        resp = self.send_request('POST', url, data)
        del self.extra_headers["Content-Type"]
        return resp

    def get(self, url):
        return self.send_request('GET', url)

    def patch(self, url, data):
        self.extra_headers["Content-Type"] = "application/json"
        resp = self.send_request('POST', url, data)
        del self.extra_headers["Content-Type"]
        return resp

    def delete(self, url):
        return self.send_request('DELETE', url)

    def set_extra_header(self, headers):
        self.extra_headers.update(headers)

    def del_extra_header(self, name):
        del self.extra_headers[name]

class HttpResponse(object):
    def __init__(self, host, http_resp):
        self.host = host
        self._body = http_resp.read()
        self._headers = {}
        for h in http_resp.info().headers:
            pos = h.find(":")
            key = h[0:pos]
            value = h[pos+1:].strip()
            self._headers[key] = value
        self._status = http_resp.code

    def _get_body(self):
        return self._body
    body = property(_get_body)

    def _get_headers(self):
        return self._headers
    headers = property(_get_headers)

    def get_header(self, name):
        if name in self.headers:
            return self.headers[name]
        return None

    def _get_status(self):
        return self._status
    status = property(_get_status)

    def get_new_location(self):
        if "Location" in self._headers:
            location = self._headers["Location"]
            pos = location.find(self.host)
            if pos == -1:
                return None
            offset = len(self.host) + pos
            return location[offset:].strip()
        return None

    def get_session_key(self):
        if "X-Auth-Token" in self._headers:
            return {"X-Auth-Token": self._headers["X-Auth-Token"]}
        return None

    def is_successful(self):
        return self.status in range(200, 204)

    def __str__(self):
        headers = ''
        for k, v in self._headers.iteritems():
            headers += "%s: %s\n" % (k, v)
        return '%(status)s\n%(headers)s\n\n%(body)s' % {'status': self.status,
         'headers': headers,
         'body': self.body}

