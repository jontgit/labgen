from urllib.request import urlopen as request_urlopen
from urllib.request import Request as request
from traceback import print_exc as traceback_print_exc
from threading import Thread
import re
from json import loads as json_loads
from json import dumps as json_dumps
from time import time
from random import randrange
from random import randint
from random import seed
from math import cos, sin, radians, sqrt
from labgen.telnet.telnet import *

IPRegex = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

ServerInitError = "Please input a server ip address and port. 'Gns3Server('127.0.0.1','80')'"
InavlidIPError = "Invalid IP address."
InvalidPortError = "Invalid Port Number."

class Timer:

    def __init__(self):
        self.timers = {}

    def toggle_timer(self, timer):
        if timer in self.timers:
            print('--- {} --- {} Seconds'.format(timer, round(time() - self.timers[timer]), 5))
        else:
            self.timers[timer] = time()

class Server:

    ###
    ### INIT FUNCTIONS
    ###

    def __init__(self, IP=None, Port=None):

        """

        Class initialisation, validates the input to ensure the ip/port are valid.
        sets the base url as an attribute, get the tempaltes from the GNS3 server,
        and then get the project data, and initilise a list for telnet threads.

        """

        self.validate_input(IP, Port)
        self.url = ('http://{}:{}/v2/'.format(self.IP, self.Port))
        self.get_templates()
        self.get_data()
        self.telnet_threads = []

    def validate_input(self, IP, Port):
        """

        Validates Server & Port information before initialisation.

        """
        exception = ServerInitError
        try:
            if IP != None:
                if re.match(IPRegex, IP):
                    self.IP = IP
                else:
                    exception = InavlidIPError
                    raise

            if Port != None:
                if int(Port) in range(0,65535):
                    self.Port = Port
                else:
                    exception = InvalidPortError
                    raise
        except:
            traceback_print_exc()

    ###
    ### UTIL FUNCTIONS
    ###

    def print_json(self, data):
        """

        Prints dictionary as formatted readable output.

        """
        data[project_name]['nodes'][node_name]['console_session'] = console_session
        print(json_dumps(data, indent=4))

    def get_circle_coords(self, radius, divider, count,center_x, center_y):

        """

        Returns a tuple (x, y) for points in a circle around a central point

        """

        angle_deg = (360/divider)*count
        angle = radians(angle_deg-(90 + (360/divider)))
        x = radius*cos(angle) + center_x;
        y = radius*sin(angle) + center_y;
        return (int(x), int(y))

    def get_field_coords(self, count, boundry_x, boundry_y, buffer):

        """

        Returns a list of tuple coordinates in a boundry range. The buffer
        is the closest distance to be allowed between two nodes. if the amount
        of nodes and the buffer are too big, we'll only do 1000 iterations to
        make sure we get out of the loop.

        """

        buffer = int(buffer/2)
        loop_count = 0
        coords = []
        while len(coords) < count:
            seed()
            x = randrange(-boundry_x, boundry_x)
            y = randrange(-boundry_y, boundry_y)

            if len(coords) == 0:
                coords.append((x, y))
            else:
                too_close_count = 0
                for coord in coords:
                    if (x not in range(coord[0]-buffer, coord[0]+buffer)) and (y not in range(coord[1]-buffer, coord[1]+buffer)):
                        too_close_count += 1
                        #if (y not in range(coord[1], coord[1]-buffer)) and (y not in range(coord[1], coord[1]+buffer)):

                    else:
                        break
                if too_close_count == len(coords):
                    coords.append((x, y))
            if loop_count > 1000:
                print('Ran out of space. Please either reduce node count or increase field size.')
                break
            else:
                loop_count += 1
        return coords

    def get_grid_coords(self, count, boundry_x, boundry_y, grid_size):

        """

        Returns a list of tuple coordinates in a boundry range. The buffer
        is the closest distance to be allowed between two nodes. if the amount
        of nodes and the buffer are too big, we'll only do 1000 iterations to
        make sure we get out of the loop.

        """

        coords = []

        boundry_x = int(boundry_x/10)
        boundry_y = int(boundry_y/10)

        while len(coords) < count:
            seed()


            x = randint(-boundry_x, boundry_x)
            y = randint(-boundry_y, boundry_y)

            if len(coords) == 0:
                coords.append((x*grid_size, y*grid_size))
            else:
                for coord in coords:
                    if (x not in range(coord[0]-buffer*grid_size, coord[0]+buffer*grid_size)) and (y not in range(coord[1]-buffer, coord[1]+buffer)):
                        pass
                    else:
                        break

    def distance(self, co1, co2):

        """

        Get the distance between two points

        """

        return sqrt(pow(abs(co1[0] - co2[0]), 2) + pow(abs(co1[1] - co2[1]), 2))

    def closest_coord(self, list, coord):

        """

        Find the closest coordinate from a list of coordinates.
        This can be used to create links between close nodes.

        """

        closest = (0,0)
        second_closest = (0,0)
        for c in list:
            if self.distance(c, coord) < self.distance(closest, coord) and (c != coord):
                second_closest = closest
                closest = c
        #print(closest, coord)
        return (closest, second_closest)

    def format_url(self, command):

        """

        Formats any commands to be sent to the server into a url.

        """

        return '{}{}'.format(self.url,command)

    ###
    ### DATA HANDLING FUNCTIONS
    ###

    def update_link_id(self, data):

        """

        Updates a given port on a node to state what other node it connects up to.

        """

        self.data[data['project_name']]['nodes'][data['first']]['ports'][data['first_port']]['link_id'] = data['link_id']
        self.data[data['project_name']]['nodes'][data['second']]['ports'][data['second_port']]['link_id'] = data['link_id']

    def get_node_name_from_id(self, project_name, node_id):

        """

        Returns a node's name based off of the node's ID. (duh)

        """

        for node in self.data[project_name]['nodes']:
            if self.data[project_name]['nodes'][node]['node_id'] == node_id:
                return node

    def get_data(self, **kwargs):

        """

        Generates class variable 'data' for manipulation by sending a HTTP request to the server
        and serializing the results based upon names, rather than the UUID's generated by GNS3.
        Contains project, node and port information with the name as the key.
        An example data structure is at the bottom of this file.


        """

        self.data = {}
        #node_data = ''
        #link_data = ''
        templates_data = self.request_from_server('templates')
        self.templates = templates_data
        project_data = self.request_from_server('projects')
        for project in project_data:
            project_name = project['name']
            if 'project_name' in kwargs:
                if project_name != kwargs['project_name']:
                    continue

            self.data[project_name] = {}
            self.data[project_name]['project_id'] = project['project_id']
            self.data[project_name]['nodes'] = {}
            node_data = self.request_from_server('projects/{}/nodes'.format(project['project_id']))
            link_data = self.request_from_server('projects/{}/links'.format(project['project_id']))
            for node in node_data:
                node_name = node['name']
                self.data[project_name]['nodes'][node_name] = {}
                self.data[project_name]['nodes'][node_name]['node_id'] = node['node_id']
                self.data[project_name]['nodes'][node_name]['template_id'] = node['template_id']
                self.data[project_name]['nodes'][node_name]['node_type'] = node['node_type']
                self.data[project_name]['nodes'][node_name]['console_port'] = node['console']
                self.data[project_name]['nodes'][node_name]['console_session'] = None
                self.data[project_name]['nodes'][node_name]['x'] = node['x']
                self.data[project_name]['nodes'][node_name]['y'] = node['y']
                self.data[project_name]['nodes'][node_name]['ports'] = {}
                if project['status'] != 'closed':
                    self.data[project_name]['nodes'][node_name]['status'] = node['status']
                    for port in node['ports']:
                        port_name = port['short_name']
                        self.data[project_name]['nodes'][node_name]['ports'][port_name] = {}
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['adapter_number'] = port['adapter_number']
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['port_number'] = port['port_number']
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['link_type'] = port['link_type']
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['link_id'] = None
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['in_use'] = False
                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['connected_to'] = None
                        for link in link_data:
                            for link_node in link['nodes']:
                                if node['node_id'] == link_node['node_id']:
                                    if link_node['label']['text'] == port_name:
                                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['link_id'] = link['link_id']
                                        self.data[project_name]['nodes'][node_name]['ports'][port_name]['in_use'] = True
                                        if link['nodes'].index(link_node) == 0:
                                            self.data[project_name]['nodes'][node_name]['ports'][port_name]['connected_to_id'] = link['nodes'][1]['node_id']
                                            self.data[project_name]['nodes'][node_name]['ports'][port_name]['connected_to'] = self.get_node_name_from_id(project_name,link['nodes'][1]['node_id'])
                                        else:
                                            self.data[project_name]['nodes'][node_name]['ports'][port_name]['connected_to_id'] = link['nodes'][0]['node_id']
                                            self.data[project_name]['nodes'][node_name]['ports'][port_name]['connected_to'] = self.get_node_name_from_id(project_name,link['nodes'][0]['node_id'])

    def get_templates(self):

        """

        Sends a HTTP request and stores the response to the class of all current templates
        that have been created on the server. needs to be properly serialized.

        """

        data = self.request_from_server('templates')
        self.templates = data

    def get_template(self ,template_name):

        """

        Reads the data in the server's templates for the name provided.
        Returns the full template, or returns None if it wasn't found.

        """

        found = False
        for template in self.templates:
            if template['name'] == template_name:
                found = True
                return template
        if not found:
            return None

    ###
    ### NODE CONTROL FUNCTIONS
    ###

    def start_node(self, **kwargs):
        # project_name, node_name

        """

        Sends a HTTP POST packet to the UUID/Url of the server to start the node.
        Sets the local server data of the node in question to 'running'

        """

        try:
            if kwargs['project_name'] in self.data:
                project_name = kwargs['project_name']
                project_id = self.data[project_name]['project_id']
                if kwargs['node_name'] in self.data[project_name]['nodes']:
                    node_name = kwargs['node_name']
                    node_id = self.data[project_name]['nodes'][node_name]['node_id']
                    resp = self.post_to_server('projects/{}/nodes/{}/start'.format(project_id, node_id),{})
                    print('Node \'{}\' started.'.format(node_name))
                    self.data[project_name]['nodes'][node_name]['status'] = "running"
        except:
            traceback_print_exc()

    def stop_node(self, **kwargs):
        # project_name, node_name

        """

        Sends a HTTP POST packet to the UUID/Url of the server to start the node.
        Sets the local server data of the node in question to '̶̶̶r̶̶̶u̶̶̶n̶̶̶n̶̶̶i̶̶̶n̶̶̶g̶̶̶'̶̶̶  'stopped'

        """

        try:
            if kwargs['project_name'] in self.data:
                project_name = kwargs['project_name']
                project_id = self.data[project_name]['project_id']
                if kwargs['node_name'] in self.data[project_name]['nodes']:
                    node_name = kwargs['node_name']
                    node_id = self.data[project_name]['nodes'][node_name]['node_id']
                    resp = self.post_to_server('projects/{}/nodes/{}/stop'.format(project_id, node_id),{})
                    print('Node \'{}\' stopped.'.format(node_name))
                    self.data[project_name]['nodes'][node_name]['status'] = "stopped"
        except:
            traceback_print_exc()

    def connect_to_node(self, **kwargs):
        # project_name, node_name

        """

        Opens a telnet connection to a node in a new thread.
        Then assigns the telnet session to the server class.
        This can be used to automate configurations with a
        given IP schema that can also be generated.

        """

        try:
            if kwargs['project_name'] in self.data:
                project_name = kwargs['project_name']
                project_id = self.data[project_name]['project_id']
                if kwargs['node_name'] in self.data[project_name]['nodes']:
                    node_name = kwargs['node_name']
                    console_port = self.data[project_name]['nodes'][node_name]['console_port']
                    console_session = Telnet(server_ip=self.IP, device_type='cisco_ios_telnet', console_port=console_port, node_name=node_name)
                    self.telnet_threads.append(console_session)
                    self.data[project_name]['nodes'][node_name]['console_session'] = console_session
                    #console_session.start()
        except:
            traceback_print_exc()

    def send_command(self, **kwargs):
        # project_name, Node_name, command

        pass

    ###
    ### GENERAL CREATE FUNCTIONS
    ###

    def create_project(self, **kwargs):
        # project_name, auto_close, auto_open, auto_start,
        # scene_height, scene_width, grid_size, drawing_grid_size,
        # show_grid, show_interface_labels, snap_to_grid

        try:
            if kwargs['project_name'] not in self.data:
                data = self.format_project_data(**kwargs)
                resp = self.post_to_server('projects',data)
                print('Project \'{}\' created.'.format(kwargs['name']))
                self.get_projects()
            else:
                raise Exception('Project {} is already present.'.format(kwargs['name']))

        except Exception as ex:
            traceback_print_exc()

    def create_node(self, **kwargs):
        # project_name, node_name,
        # node_template, x, y

        project_name = kwargs['project_name']
        node_name = kwargs['node_name']
        try:
            if kwargs['node_name'] not in self.data[project_name]['nodes']:
                data = self.format_node_data(**kwargs)
                project_id = self.data[project_name]['project_id']
                resp = self.post_to_server('projects/{}/nodes'.format(project_id),data)
                data = json_loads(resp.read().decode('utf-8'))

                node = {}
                node['node_id'] = data['node_id']
                node['template_id'] = data['template_id']
                node['node_type'] = data['node_type']
                node['console_port'] = data['console']
                node['status'] = "stopped"
                node['console_session'] = None
                node['x'] = data['x']
                node['y'] = data['y']
                node['ports'] = {}
                for port in data['ports']:
                    port_name = port['short_name']
                    node['ports'][port_name] = {}
                    node['ports'][port_name]["in_use"] = False
                    node['ports'][port_name]["connected_to"] = None
                    node['ports'][port_name]["link_type"] = port['link_type']
                    node['ports'][port_name]["adapter_number"] = port['adapter_number']
                    node['ports'][port_name]["port_number"] = port['port_number']
                self.data[project_name]['nodes'][node_name] = node
                print('Node \'{}\' created.'.format(kwargs['node_name']))

            else:
                print('Node \'{}\' is already present.'.format(kwargs['node_name']))

        except Exception as ex:
            traceback_print_exc()

    def create_template(self, **kwargs):
        # project_name, node_name,
        # node_template, x, y

        for arg in kwargs:
            if arg == 'project_name':
                project_name = kwargs[arg]
            elif arg == 'node_name':
                node_name = kwargs[arg]
            elif arg == 'node_template':
                node_template = kwargs[arg]
            elif arg == 'x':
                x = kwargs[arg]
            elif arg == 'y':
                y = kwargs[arg]

        data = {
            'name' : 'ssmemes',
            'x' : x,
            'y' : y
        }

        project_id = self.data[project_name]['project_id']
        template = self.get_template(node_template)

        if template == None:
            raise Exception('Template \'{}\' is not present on the server.'.format(node_template))

        else:
            template_id = template['template_id']

        try:
            if kwargs['node_name'] not in self.data[project_name]['nodes']:
                resp = self.post_to_server('projects/{}/templates/{}'.format(project_id,template_id),data)
                data = json_loads(resp.read().decode('utf-8'))
                node = {}
                node['node_id'] = data['node_id']
                node['template_id'] = data['template_id']
                node['node_type'] = data['node_type']
                node['console_port'] = data['console']
                node['status'] = "stopped"
                node['console_session'] = None
                node['x'] = data['x']
                node['y'] = data['y']
                node['ports'] = {}
                for port in data['ports']:
                    port_name = port['short_name']
                    node['ports'][port_name] = {}
                    node['ports'][port_name]["in_use"] = False
                    node['ports'][port_name]["connected_to"] = None
                    node['ports'][port_name]["link_type"] = port['link_type']
                    node['ports'][port_name]["adapter_number"] = port['adapter_number']
                    node['ports'][port_name]["port_number"] = port['port_number']
                print('Node \'{}\' created.'.format(kwargs['node_name']))
                self.update_node_name(project_name=project_name, node_name=node_name, node_id=data['node_id'])
                self.data[project_name]['nodes'][node_name] = node

        except:
            traceback_print_exc()

    def create_link(self, **kwargs):
        # project_name, first_node, second_node
        # first_port_name, second_port_name (Specific linking)
        # link_type (General linking)

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

                self.update_link_id(new_data)


                print('\'{}\' {} <--> {} \'{}\''.format(kwargs['first_node'], first_port, second_port, kwargs['second_node']))

        except Exception as ex:
            traceback_print_exc()

    def create_batch(self, **kwargs):
        # project_name, node_count, name_template,
        # names,node_template, layout

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
            elif arg == 'manual':
                manual = kwargs[arg]
            elif arg == 'anchor_x':
                anchor_x = kwargs[arg]
            elif arg == 'anchor_y':
                anchor_y = kwargs[arg]
            elif arg == 'field_x':
                field_x = kwargs[arg]
            elif arg == 'field_y':
                field_y = kwargs[arg]
            elif arg == 'buffer':
                buffer = kwargs[arg]

        if ('anchor_x' not in kwargs) or ('anchor_y' not in kwargs):
            anchor_x, anchor_y = 0, 0

        manual = False

        if topology == 'ring':

            for i in range(1,node_count+1):
                name = name_template.format(i)
                coords = self.get_circle_coords(radius,node_count,i,anchor_x,anchor_y)
                if manual:
                    self.create_node(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])
                else:
                    self.create_template(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])

            for i in range(1,node_count+1):
                if i != node_count:
                    name = name_template.format(i)
                    next_name = name_template.format(i+1)
                else:
                    name = name_template.format(i)
                    next_name = name_template.format(1)
                self.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)



        elif topology == 'random mesh':

            for i in range(1,node_count+1):
                name = name_template.format(i)
                if i == 1:
                    coords = (anchor_x, anchor_y)
                else:
                    coords = self.get_circle_coords(radius,node_count-1,i,anchor_x,anchor_y)
                if manual:
                    self.create_node(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])
                else:
                    self.create_template(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])

            for current_node in range(1,node_count+1):
                name = name_template.format(current_node)
                for target_node in range(current_node,node_count+1):
                    if current_node != target_node:
                        if link_chance <= randrange(0, 101, 2):
                            next_name = name_template.format(target_node)
                            self.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)

        elif topology == 'full mesh':

            for i in range(1,node_count+1):
                name = name_template.format(i)
                if i == 1:
                    coords = (anchor_x, anchor_y)
                else:
                    coords = self.get_circle_coords(radius,node_count-1,i,anchor_x,anchor_y)
                if manual:
                    self.create_node(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])
                else:
                    self.create_template(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])

            for current_node in range(1,node_count+1):
                name = name_template.format(current_node)
                for target_node in range(current_node,node_count+1):
                    if current_node != target_node:
                        next_name = name_template.format(target_node)
                        self.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)

        elif (topology == 'star') or (topology == 'hub and spoke'):

            for i in range(1,node_count+1):
                name = name_template.format(i)
                if i == 1:
                    coords = (anchor_x, anchor_y)
                else:
                    coords = self.get_circle_coords(radius,node_count-1,i,anchor_x,anchor_y)
                if manual:
                    self.create_node(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])
                else:
                    self.create_template(project_name=project_name,node_name=name,node_template=node_template,x=coords[0],y=coords[1])

            for current_node in range(2,node_count+1):
                name = name_template.format(1)
                next_name = name_template.format(current_node)
                self.create_link(project_name=project_name, first_node=name, second_node=next_name, link_type=link_type)

        elif topology == 'wan':
            # pass, get_field_coords

            nodes = []
            links = []

            coordinates = self.get_field_coords(node_count, field_x, field_y, buffer)
            #print(coordinates)
            for i, coord in enumerate(coordinates, 1):
                name = name_template.format(i)
                self.create_template(project_name=project_name,node_name=name,node_template=node_template,x=coord[0],y=coord[1])
                nodes.append({
                    'name' : name,
                    'coords' : coord
                })

            for i, coord in enumerate(coordinates, 1):
                name = name_template.format(i)
                #print(coordinates)
                #next_name = ''
                closest = self.closest_coord(coordinates, coord)[0]
                second_closest = self.closest_coord(coordinates, coord)[1]
                for c, node in enumerate(nodes):
                    if (node['coords'] == closest):

                        next_name = node['name']

                print('Node: {} Closest: {}'.format(name, next_name))
                #print(closest)
                #next_name = name_template.format(current_node)

                #for link in links:
                #    if name == link[0]:


                self.create_link(project_name=project_name,
                                 first_node=name,
                                 second_node=next_name,
                                 link_type=link_type)

                links.append((name, next_name))



        elif topology == 'hierachical':
            pass

        elif topology == 'chain':
            pass

    def update_node_name(self, **kwargs):
        try:
            for arg in kwargs:
                if arg == 'project_name':
                    project_name = kwargs[arg]
                elif arg == 'node_name':
                    node_name = kwargs[arg]
                elif arg == 'node_id':
                    node_id = kwargs[arg]

            project_id = self.data[project_name]['project_id']
            data = { 'name' : node_name }
            #print('Attempting to change {} - {}'.format(node_name,node_id))
            resp = self.put_to_server('projects/{}/nodes/{}'.format(project_id, node_id),data)
            data = json_loads(resp.read().decode('utf-8'))
        except Exception as ex:
            traceback_print_exc()

    def draw_text(self, **kwargs):
        rotation = 0
        for arg in kwargs:
            if arg == 'project_name':
                project_name = kwargs[arg]
            elif arg == 'x':
                x = kwargs[arg]
            elif arg == 'y':
                y = kwargs[arg]
            elif arg == 'text':
                text = kwargs[arg]
            elif arg == 'font_size':
                font_size = kwargs[arg]
            elif arg == 'rotation':
                rotation = kwargs[arg]
            elif arg == 'colour':
                colour = kwargs[arg]
        try:
            project_id = self.data[project_name]['project_id']
        except:
            print('Error: {} not found.'.format(project_name))

        svg = "<svg width=\"{}\" height=\"{}\"><text fill=\"{}\" fill-opacity=\"{}\" font-family=\"{}\" font-size=\"{}\" font-weight=\"{}\">{}</text></svg>".format(100, 100, '#000000', 1.0, "TypeWriter", font_size, 'bold', text)
        #"<svg height=\"88\" width=\"53\"><text fill=\"#000000\" fill-opacity=\"1.0\" font-family=\"TypeWriter\" font-size=\"10.0\" font-weight=\"bold\">Memes\n\n\n\n</text></svg>"

        data = {
            'rotation' : rotation,
            'x' : x,
            'y' : y,
            'svg' : svg,
        }
        print(data)
        resp = self.post_to_server('projects/{}/drawings'.format(project_id),data)
        data = json_loads(resp.read().decode('utf-8'))

    def draw_line(self, **kwargs):

        for arg in kwargs:
            if arg == 'project_name':
                project_name = kwargs[arg]
            elif arg == 'x':
                x = kwargs[arg]
            elif arg == 'y':
                y = kwargs[arg]
            elif arg == 'height':
                height = kwargs[arg]
            elif arg == 'width':
                width = kwargs[arg]
            elif arg == 'colour':
                colour = kwargs[arg]

        try:
            project_id = self.data[project_name]['project_id']
        except:
            print('Error: {} not found.'.format(project_name))

        svg = "<svg width=\"{}\" height=\"{}\"><line stroke=\"{}\" stroke-width=\"{}\" x1=\"{}\" x2=\"{}\" y1=\"{}\" y2=\"{}\"/></svg>".format(width, height, colour, 2, 0, width, 0, height)

        data = {
            'x' : x,
            'y' : y,
            'svg' : svg,
        }
        print(data)
        resp = self.post_to_server('projects/{}/drawings'.format(project_id),data)
        data = json_loads(resp.read().decode('utf-8'))

    ###
    ### PROJECT CREATE FUNCTIONS
    ###

    #def create_3_tier_site(self, **kwargs):

    ###
    ### DELETE FUNCTIONS
    ###

    def delete_project(self, project_name=None):
        project_id = ''
        try:
            if name in self.names_ids:
                resp = self.delete_from_server('projects/{}'.format(self.names_ids[project_name]['project_id']))
                print('Project \'{}\' deleted.'.format(project_name))
                self.get_projects()
            else:
                raise Exception('Project \'{}\' is not present.'.format(project_name))

        except Exception as ex:
            print(ex)

    def delete_node(self, project_name=None, node_name=None):
        try:
            if node_name in self.data[project_name]['nodes']:
                project_id = self.data[project_name]['project_id']
                node_id = self.data[project_name]['nodes'][node_name]
                resp = self.delete_from_server('projects/{}/nodes/{}'.format(project_id, node_id))
                self.get_projects()
                print('Node \'{}\' deleted.'.format(node_name))

            else:
                raise Exception('Node \'{}\' is not present.'.format(node_name))

        except Exception as ex:
            print(ex)

    def delete_all_nodes(self, project_name):
        try:
            project_id = self.data[project_name]['project_id']
            for node in self.data[project_name]['nodes']:
                node_id = self.data[project_name]['nodes'][node]['node_id']
                resp = self.delete_from_server('projects/{}/nodes/{}'.format(project_id, node_id))
                print('Node \'{}\' deleted.'.format(node))
            self.get_projects()
        except:
            print('Error: Project {} not found.'.format(project_name))

    ###
    ### DATA FORMAT FUNCTIONS
    ###

    def format_node_data(self, **kwargs):
        data = {}
        data['properties'] = {}
        new_name = ''
        template = ''
        try:
            for arg in kwargs:

                if arg == 'project_name':
                    continue

                elif arg == 'node_template':
                    template = self.get_template(kwargs['node_template'])
                    if template == None:
                        raise Exception('Template \'{}\' does not exsist'.format(arg))

                elif arg == 'node_name':
                    new_name = kwargs[arg]

                elif arg == 'x':
                    data['x'] = kwargs[arg]

                elif arg == 'y':
                    data['y'] = kwargs[arg]

                else:
                    raise Exception('Key error in node creation: {}'.format(arg))

            for entry in template.keys():
                if re.match('(slot\d+)|(wic\d+)|(system_id)|(nvram)|(ram)|(image)|(platform)|(idlepc)|(startup_config_content)', entry):
                    data['properties'][entry] = template[entry]

                if re.match('(adapters)', entry):
                    data['properties'][entry] = template[entry]

                if re.match('(first_port_name)|(port_name_format)', entry):
                    data[entry] = template[entry]

            data['symbol'] = template['symbol']
            data['name'] = new_name
            data['compute_id'] = template['compute_id']
            data['node_type'] = template['template_type']
            return data

        except Exception as ex:
            traceback_print_exc()
            print(ex)

    def format_project_data(self, **kwargs):
        data = {}
        try:
            for arg in kwargs:
                if arg == 'project_name':
                    data['name'] = kwargs[arg]
                elif arg == 'auto_close':
                    data['auto_close'] = kwargs[arg]
                elif arg == 'auto_open':
                    data['auto_open'] = kwargs[arg]
                elif arg == 'auto_start':
                    data['auto_start'] = kwargs[arg]
                elif arg == 'scene_height':
                    data['scene_height'] = kwargs[arg]
                elif arg == 'scene_width':
                    data['scene_width'] = kwargs[arg]
                elif arg == 'grid_size':
                    data['grid_size'] = kwargs[arg]
                elif arg == 'drawing_grid_size':
                    data['drawing_grid_size'] = kwargs[arg]
                elif arg == 'show_grid':
                    data['show_grid'] = kwargs[arg]
                elif arg == 'show_interface_labels':
                    data['show_interface_labels'] = kwargs[arg]
                elif arg == 'snap_to_grid':
                    data['snap_to_grid'] = kwargs[arg]
                else:
                    raise Exception('Key error in project creation: {}'.format(arg))
            return data

        except Exception as ex:
            print(ex)

    def format_link_data(self, **kwargs):

        try:
            links = ''
            link_found = False
            data = {
                "nodes" : [{'label':{}},{'label':{}}]
            }
            nodes = ''
            project_id = ''
            for arg in kwargs:

                if arg == 'project_name':
                    project_name = kwargs[arg]
                    project_id = self.data[kwargs[arg]]['project_id']
                    nodes = self.data[project_name]['nodes']

                elif arg == 'first_node':
                    first_node = kwargs[arg]
                    data["nodes"][0]['node_id'] = nodes[kwargs[arg]]['node_id']

                elif arg == 'first_port_name':
                    first_port_name = kwargs[arg]
                    first_port = self.data[project_name]['nodes'][first_node]['ports'][first_port_name]
                    data["nodes"][0]['adapter_number'] = first_port['adapter_number']
                    data["nodes"][0]['port_number'] = first_port['port_number']
                    data["nodes"][0]['label']['text'] = first_port_name
                    link_type = first_port['link_type']

                elif arg == 'second_node':
                    second_node = kwargs[arg]
                    data["nodes"][1]['node_id'] = nodes[second_node]['node_id']

                elif arg == 'second_port_name':
                    second_port_name = kwargs[arg]
                    second_port = self.data[project_name]['nodes'][second_node]['ports'][second_port_name]
                    data["nodes"][1]['adapter_number'] = second_port['adapter_number']
                    data["nodes"][1]['port_number'] = second_port['port_number']
                    data["nodes"][1]['label']['text'] = second_port_name

                elif arg == 'link_type':
                    link_type = kwargs[arg]
                    link_found = False
                    for port in self.data[project_name]['nodes'][first_node]['ports']:
                        first_in_use = self.data[project_name]['nodes'][first_node]['ports'][port]['in_use']
                        first_link_type = self.data[project_name]['nodes'][first_node]['ports'][port]['link_type']
                        if (first_in_use == False) and (first_link_type == link_type):
                            data["nodes"][0]['adapter_number'] = self.data[project_name]['nodes'][first_node]['ports'][port]['adapter_number']
                            data["nodes"][0]['port_number'] = self.data[project_name]['nodes'][first_node]['ports'][port]['port_number']
                            data["nodes"][0]['label']['text'] = port
                            self.data[project_name]['nodes'][first_node]['ports'][port]['in_use'] = True
                            self.data[project_name]['nodes'][first_node]['ports'][port]['connected_to'] = kwargs['second_node']
                            self.data[project_name]['nodes'][first_node]['ports'][port]['connected_to_id'] = self.data[project_name]['nodes'][kwargs['second_node']]['node_id']
                            self.data[project_name]['nodes'][first_node]['ports'][port]['link_id'] = 'memes'
                            link_found = True
                            break
                        else:
                            pass

                    for port in self.data[project_name]['nodes'][kwargs['second_node']]['ports']:
                        second_in_use = self.data[project_name]['nodes'][kwargs['second_node']]['ports'][port]['in_use']
                        second_link_type = self.data[project_name]['nodes'][kwargs['second_node']]['ports'][port]['link_type']
                        if (second_in_use == False) and (second_link_type == link_type):
                            data["nodes"][1]['adapter_number'] = self.data[project_name]['nodes'][second_node]['ports'][port]['adapter_number']
                            data["nodes"][1]['port_number'] = self.data[project_name]['nodes'][second_node]['ports'][port]['port_number']
                            data["nodes"][1]['label']['text'] = port
                            self.data[project_name]['nodes'][second_node]['ports'][port]['in_use'] = True
                            self.data[project_name]['nodes'][second_node]['ports'][port]['connected_to'] = kwargs['first_node']
                            self.data[project_name]['nodes'][second_node]['ports'][port]['connected_to_id'] = self.data[project_name]['nodes'][kwargs['first_node']]['node_id']
                            self.data[project_name]['nodes'][second_node]['ports'][port]['link_id'] = 'memes'
                            link_found = True
                            break
                        else:
                            pass

            #if (first_link_type or second_link_type):
            #    raise Exception('No links of type \'{}\'.'.format(link_type))

            if not link_found:
                raise Exception('No ports free')
            else:
                return data

        except:
            traceback_print_exc()

    ###
    ### HTTP FUNCTIONS
    ###

    def put_to_server(self, command, input_data):
        url = self.format_url(command)
        data = str(json_dumps(input_data)).encode('utf-8')
        req = request(url, method='PUT', data=data)
        resp = request_urlopen(req)
        return resp

    def post_to_server(self, command, input_data):
        url = self.format_url(command)
        data = str(json_dumps(input_data)).encode('utf-8')
        req = request(url, data=data)
        resp = request_urlopen(req)
        return resp

    def request_from_server(self, command):
        url = self.format_url(command)
        req = request_urlopen(url)
        data = json_loads(req.read().decode('utf-8'))
        return data

    def delete_from_server(self, command):
        url = self.format_url(command)
        req = request(url, method='DELETE')
        resp = request_urlopen(req)
        return resp

if __name__ == "__main__":

    server = Gns3Server('10.255.10.30', '80')
    server.create_batch(project_name='APITest', node_count=7, radius=200, name_template='Test_node_{}', node_template='2691', layout='circle', link_type='serial', topology='full mesh')
    #server.create_link(project_name='APITest',first_nodelink_type='serial')
    #server.print_json(server.data['APITest']) ,names=['Test_node_1a','Test_node_2a','Test_node_3a']
    #server.create_link()

    #print(json_dumps(server.data['APITest'], indent=4))


"""

Example local data:
{
    "untitled": {
        "nodes": {},
        "project_id": "225af93a-5df4-401e-9500-a81be776be41"
    },
    "Fortigate": {
        "nodes": {},
        "project_id": "0dc05d35-e0b5-462e-8f23-1f9e34180216"
    },
    "WAN 2": {
        "nodes": {},
        "project_id": "70cbebb3-e16d-404c-8bbd-0ec8454e547b"
    },
    "APITest": {
        "nodes": {
            "Test_node_1": {
                "node_id": "4357a4f9-1650-44a9-b902-e48e92f3ab06",
                "ports": {
                    "f0/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 0
                    },
                    "f0/1": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 1
                    },
                    "f1/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 1,
                        "port_number": 0
                    }
                }
            },
            "Test_node_2": {
                "node_id": "2354bf48-a478-407f-a997-be22ee59f5a7",
                "ports": {
                    "f0/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 0
                    },
                    "f0/1": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 1
                    },
                    "f1/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 1,
                        "port_number": 0
                    }
                }
            },
            "Test_node_3": {
                "node_id": "743c7e6b-cc4f-4e00-b157-6fbf98854256",
                "ports": {
                    "f0/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 0
                    },
                    "f0/1": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 0,
                        "port_number": 1
                    },
                    "f1/0": {
                        "in_use": false,
                        "connected_to": null,
                        "type": "ethernet",
                        "adapter_number": 1,
                        "port_number": 0
                    }
                }
            }
        },
        "project_id": "515bfa2f-896a-48c7-945b-acbdbbf05a38"
    },
}
_-_/
"""
