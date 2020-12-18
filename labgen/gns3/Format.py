
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
