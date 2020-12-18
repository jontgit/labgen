from os import path
from json import dump
from json import dumps

from .http import HTTP
from .util import Util

class Data:

    def GetData(**kwargs):

        """

        Generates class variable 'data' for manipulation.
        Contains project, node and port information with the name as reference.
        An example data structure is at the top.

        """

        for arg in kwargs:
            if arg == 'url':
                url = kwargs[arg]

        data = {}
        #node_data = ''
        #link_data = ''
        #templates_data = self.request_from_server('templates')
        #self.templates = templates_data
        project_data = HTTP.request_from_server(url, 'projects')
        for project in project_data:

            if 'project_name' in kwargs:
                if project['name'] != kwargs['project_name']:
                    continue

            data[project['name']] = {}
            data[project['name']]['project_id'] = project['project_id']
            data[project['name']]['nodes'] = {}
            node_data = HTTP.request_from_server(url, 'projects/{}/nodes'.format(project['project_id']))
            link_data = HTTP.request_from_server(url, 'projects/{}/links'.format(project['project_id']))
            for node in node_data:
                data[project['name']]['nodes'][node['name']] = {}
                data[project['name']]['nodes'][node['name']]['node_id'] = node['node_id']
                data[project['name']]['nodes'][node['name']]['template_id'] = node['template_id']
                data[project['name']]['nodes'][node['name']]['node_type'] = node['node_type']
                #data[project['name']]['nodes'][node['name']]['console_port'] = node['console_port']
                data[project['name']]['nodes'][node['name']]['x'] = node['x']
                data[project['name']]['nodes'][node['name']]['y'] = node['y']
                data[project['name']]['nodes'][node['name']]['ports'] = {}
                if project['status'] != 'closed':
                    for port in node['ports']:
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']] = {}
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['adapter_number'] = port['adapter_number']
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['port_number'] = port['port_number']
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['link_type'] = port['link_type']
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['link_id'] = None
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['in_use'] = False
                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['connected_to'] = None
                        for link in link_data:
                            for link_node in link['nodes']:
                                if node['node_id'] == link_node['node_id']:
                                    if link_node['label']['text'] == port['short_name']:
                                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['link_id'] = link['link_id']
                                        data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['in_use'] = True
                                        if link['nodes'].index(link_node) == 0:
                                            data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['connected_to_id'] = link['nodes'][1]['node_id']
                                            #data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['connected_to'] = self.get_node_name_from_id(project['name'],link['nodes'][1]['node_id'])
                                        else:
                                            data[project['name']]['nodes'][node['name']]['ports'][port['short_name']]['connected_to_id'] = link['nodes'][0]['node_id']

        return data

    def UpdateFile(server,port,data):
        pass

    def WriteData(server,port,data):
        current_path = path.abspath('.')
        with open('{}/data/{}_{}.json'.format(current_path,server,port), 'w') as data_file:
            #data = dumps(data, indent=4)
            dump(data, data_file)


"""
    def get_templates(self):
        data = self.request_from_server('templates')
        self.templates = data

    def get_template(self,template_name):
        found = False
        for template in self.templates:
            if template['name'] == template_name:
                found = True
                return template
        if not found:
            return None
"""
