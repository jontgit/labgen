
class Format:

    def format_project_data(**kwargs):
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
"""
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
                        #print(port)
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

            if not link_found:
                raise Exception('No ports free')
            else:
                return data

        except:
            traceback_print_exc()
"""
