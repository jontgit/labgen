from netmiko import ConnectHandler
from time import sleep
from traceback import print_exc as traceback_print_exc
import threading
class Telnet(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        #self.setDaemon(True)
        # device_type, server_ip, console_port
        for arg in kwargs:
            if arg == 'device_type':
                self.device_type = kwargs[arg]
            elif arg == 'server_ip':
                self.server_ip = kwargs[arg]
            elif arg == 'console_port':
                self.console_port = kwargs[arg]
            elif arg == 'node_name':
                self.node_name = kwargs[arg]

        self.device = {
            'device_type' : self.device_type,
            'host' : '10.255.10.30',
            'username' : '',
            'password' : '',
            'port' : 5024          # optional, defaults to 22
        }

        #self.connection = Telnet(**self.device)
        self.connected = False
        self.timed_out = False

    def run(self):
        self.open_connection()

    def open_connection(self):
        for i in range(15):
            try:
                sleep(1)
                net_connect = ConnectHandler(**self.device)
                self.connection = net_connect
                self.connected = True
                break
            except:
                pass
        if not self.connected:
            self.timed_out = True

    def run_commands(self,commands):
        output = []
        for command in commands:
            data = self.run_command(command)
            output.append(data)
        return output

    def run_command(self,command):
        try:
            output = self.connection.send_command(command)
            return output
        except:
            traceback_print_exc()

if __name__ == "__main__":
    r1 = Telnet(server_ip='10.255.10.30', device_type='cisco_ios_telnet', console_port=5024)
#    r2 = Telnet(server_ip='10.255.10.30',device_type='cisco_ios_telnet',console_port=5010)
    r1.open_connection()
    print(r1.run_command('sh ip int br'))
    #print(r2.run_command('sh ip int br'))
