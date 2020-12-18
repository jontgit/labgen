from netmiko import ConnectHandler
import threading
class Telnet(threading.Thread):
    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        for arg in kwargs:
            if arg == 'hostname':
                self.hostname = kwargs[arg]
            elif arg == 'device_type':
                self.device_type = kwargs[arg]
            elif arg == 'server_ip':
                self.server_ip = kwargs[arg]
            elif arg == 'console_port':
                self.console_port = kwargs[arg]
            elif arg == 'command':
                self.command = kwargs[arg]
            elif arg == 'commands':
                self.commands = kwargs[arg]

        self.device = {
            'device_type': self.device_type,
            'host':   self.server_ip,
            'username' : '',
            'password' : '',
            'port' : self.console_port          # optional, defaults to 22
        }
        self.run()

    def run(self):
        self.open_connection()

    def open_connection(self):
        net_connect = ConnectHandler(**self.device)
        self.connection = net_connect
        self.run_commands(['\r','\r'])

    def run_commands(self,commands):
        output = []
        for command in commands:
            data = self.run_command(command)
            output.append(data)
        return output

    def run_command(self,command):
        output = self.connection.send_command(command)
        return output

if __name__ == "__main__":
    r1 = Telnet(server_ip='10.255.10.30',device_type='cisco_ios_telnet',console_port=5009)
    r2 = Telnet(server_ip='10.255.10.30',device_type='cisco_ios_telnet',console_port=5010)
    print(r1.run_command('sh ip int br'))
    print(r2.run_command('sh ip int br'))
