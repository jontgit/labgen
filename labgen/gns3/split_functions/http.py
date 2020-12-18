
from urllib.request import urlopen as request_urlopen
from urllib.request import Request as request
from json import loads as json_loads
from json import dumps as json_dumps
from .util import Util

class HTTP:

    def post_to_server(url, command, input_data):
        url = Util.FormatUrl(url, command)
        data = str(json_dumps(input_data)).encode('utf-8')
        req = request(url, data=data)
        resp = request_urlopen(req)
        return resp

    def request_from_server(url, command):
        url = Util.FormatUrl(url, command)
        req = request_urlopen(url)
        data = json_loads(req.read().decode('utf-8'))
        return data
"""
    def delete_from_server(self, command):
        url = self.format_url(command)
        req = request(url, method='DELETE')
        resp = request_urlopen(req)
        return resp
"""
