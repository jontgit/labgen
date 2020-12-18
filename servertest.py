import labgen, json, time
server = labgen.gns3.Server("10.255.10.30", 80)
#server.create_batch(project_name='APITest',node_count=7,radius=200,name_template='R{}',node_template='IOSv',layout='circle',link_type='ethernet',topology='hub and spoke',anchor_x=-500,anchor_y=0)
server.create_batch(project_name='APITest',node_count=9,radius=200,name_template='RR{}',node_template='IOSv',layout='circle',link_type='ethernet',topology='wan',field_x=500,field_y=300, buffer=100)
#server.create_batch(project_name='APITest',node_count=6,radius=200,name_template='RS{}',node_template='IOSv',layout='circle',link_type='ethernet',topology='full mesh',anchor_x=500,anchor_y=0)
#server.create_template(project_name='APITest',node_name='R1',node_template='2691',x=0,y=0)
#time.sleep(2)
#server.start_node(project_name='APITest', node_name='R1')
#server.start_node(project_name='APITest', node_name='R2')
#server.stop_node(project_name='APITest', node_name='Test_node_1')
#print(server.print_json(server.data['APITest']))
#print(json.dumps(server.data['APITest'],indent=4))

#http://10.255.10.30/v2/projects/8743585a-b46c-47b4-b6cf-5938a240fa06/files/project-files/dynamips/8f8f0b3c-bf7c-4d58-bdbf-52fec719fdd9/configs/i1_startup-config.cfg
