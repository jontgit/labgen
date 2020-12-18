
from .Format import *
from .Http import *

class Create():
    def __init__(self, server):
        self.server = server

    def Project(**kwargs):
        # project_name, auto_close, auto_open, auto_start, scene_height, scene_width, grid_size, drawing_grid_size, show_grid, show_interface_labels, snap_to_grid)
        try:
            if kwargs['project_name'] not in self.server.data:
                data = Format.format_project_data(kwargs)
                resp = Http.post_to_server('projects',data)
                print('Project \'{}\' created.'.format(kwargs['name']))
                self.server.get_data()
            #return resp

        #    else:
        #        raise Exception('Project {} is already present.'.format(kwargs['name']))

        except Exception as ex:
            traceback_print_exc()
