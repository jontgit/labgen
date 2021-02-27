import labgen
server = labgen.gns3.Server("10.255.10.30", 80)
#server.create_batch(project_name='APITest',node_count=9,radius=200,name_template='IOSv{}',node_template='IOSv',link_type='ethernet',topology='wan',layout='circle',field_x=500,field_y=300, buffer=100)

#server.draw_line(project_name='APITest',x=-300, y=-200, height=40, width=200, colour='#000000')




server.delete_all_nodes('APITest')

"""
server.create_batch(project_name='APITest',
                    anchor_x=-500,
                    anchor_y=0,
                    node_count=7,
                    radius=200,
                    name_template='IOSv_0_{}',
                    node_template='IOSv',
                    link_type='ethernet',
                    topology='star')

server.create_batch(project_name='APITest',
                    anchor_x=0,
                    anchor_y=0,
                    node_count=9,
                    radius=200,
                    name_template='IOSv_1_{}',
                    node_template='IOSv',
                    link_type='ethernet',
                    topology='full mesh')

server.create_batch(project_name='APITest',
                    anchor_x=500,
                    anchor_y=0,
                    node_count=8,
                    radius=200,
                    name_template='IOSv_2_{}',
                    node_template='IOSv',
                    link_type='ethernet',
                    topology='ring')
"""
#http://10.255.10.30/v2/projects/8743585a-b46c-47b4-b6cf-5938a240fa06/files/project-files/dynamips/8f8f0b3c-bf7c-4d58-bdbf-52fec719fdd9/configs/i1_startup-config.cfg
