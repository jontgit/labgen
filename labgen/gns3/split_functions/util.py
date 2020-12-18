
from os import path
from json import dump

class Util:

    def FormatUrl(url, command):
        return '{}{}'.format(url, command)

    def WriteData(server,port,data):
        current_path = path.abspath('.')
        with open('{}/data/{}_{}.data'.format(current_path,server,port), 'w') as data_file:
            dump(data, data_file)
