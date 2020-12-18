
from json import loads as json_loads
from traceback import print_exc as traceback_print_exc

from .format import Format
from .http import HTTP
from .data import Data

#class Create:

#    def __init__(self, url, data):
#        self.url = url
#        self.data = data

def Project(self, **kwargs):
    # project_name, auto_close, auto_open, auto_start, scene_height, scene_width, grid_size, drawing_grid_size, show_grid, show_interface_labels, snap_to_grid)

    try:
        data = Format.format_project_data(**kwargs)
        resp = HTTP.post_to_server(self.url, 'projects',data)
        print('Project \'{}\' created.'.format(kwargs['project_name']))
        return_data = json_loads(resp.read().decode('utf-8'))

        new_project_data = {
            'project_id' : return_data['project_id'],
            'nodes' : return_data['nodes']
        }

        return data[new_project_data]

    except Exception as ex:
        traceback_print_exc()
"""
    def Node(self, **kwargs):
        # project_name, node_name, node_template, x, y
        project_name = kwargs['project_name']
        node_name = kwargs['node_name']
        try:
            if kwargs['node_name'] not in self.data[project_name]['nodes']:
                data = self.format_node_data(**kwargs)
                project_id = self.data[project_name]['project_id']
                resp = self.post_to_server('projects/{}/nodes'.format(project_id),data)
                data = json_loads(resp.read().decode('utf-8'))
                #node =
                node = {}
                node['node_id'] = data['node_id']
                node['ports'] = {}
                for port in data['ports']:
                    node['ports'][port['short_name']] = {}
                    node['ports'][port['short_name']]["in_use"] = False
                    node['ports'][port['short_name']]["connected_to"] = None
                    node['ports'][port['short_name']]["link_type"] = port['link_type']
                    node['ports'][port['short_name']]["adapter_number"] = port['adapter_number']
                    node['ports'][port['short_name']]["port_number"] = port['port_number']
                self.data[project_name]['nodes'][node_name] = node
                #self.print_json(json_loads(resp.read().decode('utf-8')))

                print('Node \'{}\' created.'.format(kwargs['node_name']))
                #server.get_data(project_name=project_name)
                #self.print_json(data)

            else:
                print('Node \'{}\' is already present.'.format(kwargs['node_name']))

        except Exception as ex:
            traceback_print_exc()

    def Link(self, **kwargs):
        # project_name, first_node, second_node
        # first_port_name, second_port_name (Specific linking)
        # link_type (General linking)
        self.timer('create_link')

        try:
            data = self.format_link_data(**kwargs)

            if data != None:
                project_id = self.data[kwargs['project_name']]['project_id']
                resp = self.post_to_server('projects/{}/links'.format(project_id),data)
                data = json_loads(resp.read().decode('utf-8'))
                first_port = data['nodes'][0]['label']['text']
                second_port = data['nodes'][1]['label']['text']
                new_data = {
                    'project_name' : kwargs['project_name'],
                    'link_id' : data['link_id'],
                    'first' : kwargs['first_node'],
                    'second' : kwargs['second_node'],
                    'first_port' : first_port,
                    'second_port' : second_port
                }
                if resp.code == '400':
                    self.print_json(data)
                #self.data[project_name]['nodes'][second_node]['ports'][port]['link_id']
                #link_id = self.get_link_id(kwargs['project_name'],get_node_name_from_id(kwargs['project_name'], kwargs['first_node']))
                self.update_link_id(new_data)

                self.timer('create_link')
                print('\'{}\' {} <--> {} \'{}\''.format(kwargs['first_node'], first_port, second_port, kwargs['second_node']))

        except Exception as ex:
            traceback_print_exc()

    def Batch(self, **kwargs):
        # server.create_batch(project_name='APITest',node_count=3,name_template='Test_node_{}',names=['Test_node_1','Test_node_2','Test_node_3'],node_template='2691',layout='circle')
        for arg in kwargs:
            if arg == 'project_name':
                project_name = kwargs[arg]
            elif arg == 'node_count':
                node_count = kwargs[arg]
            elif arg == 'name_template':
                name_template = kwargs[arg]
            elif arg == 'names':
                names = kwargs[arg]
            elif arg == 'node_template':
                node_template = kwargs[arg]
            elif arg == 'layout':
                layout = kwargs[arg]
            elif arg == 'topology':
                topology = kwargs[arg]
            elif arg == 'link_type':
                link_type = kwargs[arg]
            elif arg == 'link_chance':
                link_chance = kwargs[arg]
            elif arg == 'radius':
                radius = kwargs[arg]

        for i in range(1,node_count+1):
            name = name_template.format(i)
            coords = self.get_circle_coords(radius,node_count,i,0,0)
            server.create_node(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])

        if topology == 'ring':
            for i in range(1,node_count+1):
                if i != node_count:
                    name = name_template.format(i)
                    next_name = name_template.format(i+1)
                else:
                    name = name_template.format(i)
                    next_name = name_template.format(1)
                server.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)

        elif topology == 'partial mesh':
            for current_node in range(1,node_count+1):
                name = name_template.format(current_node)
                for target_node in range(current_node,node_count+1):
                    if current_node != target_node:
                        if link_chance <= randrange(0, 101, 2):
                            next_name = name_template.format(target_node)
                            server.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)


        elif topology == 'full mesh':
            for current_node in range(1,node_count+1):
                name = name_template.format(current_node)
                for target_node in range(current_node,node_count+1):
                    if current_node != target_node:
                        next_name = name_template.format(target_node)
                        server.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)
"""
