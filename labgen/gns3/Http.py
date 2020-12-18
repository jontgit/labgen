from urllib.request import urlopen as request_urlopen
from urllib.request import Request as request
from json import dumps as json_dumps
from json import loads as json_loads

class Http:

    def format_url(url, command):

        """

        Formats any commands to be sent to the server into a url.

        """

        return '{}{}'.format(url,command)

    def post_to_server(url, command, input_data):
        url = format_url(url, command)
        data = str(json_dumps(input_data)).encode('utf-8')
        req = request(url, data=data)
        resp = request_urlopen(req)
        data = json_loads(resp.read().decode('utf-8'))
        return data

    def request_from_server(url, command):
        url = format_url(url, command)
        req = request_urlopen(url)
        data = json_loads(req.read().decode('utf-8'))
        return data

    def delete_from_server(url, command):
        url = format_url(url, command)
        req = request(url, method='DELETE')
        resp = request_urlopen(req)
        return resp
