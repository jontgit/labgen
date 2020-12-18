from telnetlib import Telnet as TelnetLib
from netmiko import ConnectHandler
from traceback import print_exc as traceback_print_exc
import getpass
import regex
import re
import threading
import json
import time

# (R1#\n){1}?(.+\n){0,}(?!R1#$)
# (?<=R1#.*\n)(.*\n)*?(?=R1#.*\n?|$)   (?<={}#.*\n)(.*\n)*?(?={}#.*\n?)
#

class Dynamips:
    def __init__(self, hostname):
        self.hostname = hostname
        self.user_login = ('Username:\s').encode('ascii')                                                       # 'Username: '
        self.user_password = ('Password:\s').encode('ascii')                                                    # 'Password: '
        self.user_exec = ('({})(>)'.format(self.hostname)).encode('ascii')                                      # 'cisco>'
        self.priv_exec = ('({})(#)$'.format(self.hostname)).encode('ascii')                                     # 'cisco#'
        self.config_mode = ('({})(\(\w+\))(#)'.format(self.hostname)).encode('ascii')                           # 'cisco(config)#'
        self.internal_config_mode = ('({})(\(([\w-]+)\))(#)'.format(self.hostname)).encode('ascii')             # 'cisco(config-int)#'
        self.last_input = regex.compile('(?<={}#.*\n)(.*\n)*?(?={}#.*\n?)'.format(self.hostname, self.hostname).encode('ascii')) # Matches last output - telnet sessions don't close for dynamips routers
        self.eol = regex.compile('{}#$'.format(self.hostname).encode('ascii'))

        self.regex = [self.user_login,
                      self.user_password,
                      self.user_exec,
                      self.priv_exec,
                      self.config_mode,
                      self.internal_config_mode]

    def get_last_output(self):
        return self.last_input

    def set_interface_ip(self, interface, ip, mask):
        return ['conf t',
                'interface {}'.format(interface),
                'ip addr {} {}'.format(ip, mask),
                'end']

    def set_default_route(self, args):
        gateway = args[0]
        return ['conf t',
                'ip route 0.0.0.0 0.0.0.0 {}'.format(gateway),
                'end']

class Cisco_IOS:
    def __init__(self, hostname):
        self.hostname = hostname
        self.user_login = ('Username:\s').encode('ascii')                                                       # 'Username: '
        self.user_password = ('Password:\s').encode('ascii')                                                    # 'Password: '
        self.user_exec = ('({})(>)'.format(self.hostname)).encode('ascii')                                      # 'cisco>'
        self.priv_exec = ('({})(#)[\s]*$'.format(self.hostname)).encode('ascii')                                # 'cisco#'
        self.config_mode = ('({})(\(\w+\))(#)'.format(self.hostname)).encode('ascii')                           # 'cisco(config)#'
        self.internal_config_mode = ('({})(\(([\w-]+)\))(#)'.format(self.hostname)).encode('ascii')             # 'cisco(config-int)#'

        self.regex = [self.user_login,
                      self.user_password,
                      self.user_exec,
                      self.priv_exec,
                      self.config_mode,
                      self.internal_config_mode]


    def set_interface_p2p(self, interface, proto):
        return ['conf t',
                'interface {}'.format(interface),
                'encapsulation {}'.format(proto),
                'end']


    def set_interface_ip(self, interface, ip, mask):
        return ['conf t',
                'interface {}'.format(interface),
                'ip addr {} {}'.format(ip, mask),
                'end']

    def set_default_route(self, args):
        gateway = args[0]
        return ['conf t',
                'ip route 0.0.0.0 0.0.0.0 {}'.format(gateway),
                'end']

class FortiGate:
    def __init__(self, hostname):
        self.hostname = hostname
        self.user_login = ('({})\slogin:\s'.format(self.hostname)).encode('ascii')                              # 'FortiGate login: '
        self.user_password = ('Password:\s').encode('ascii')                                                    # 'Password: '
        self.user_exec = ('({})\s#\s'.format(self.hostname)).encode('ascii')                                    # 'FortiGate # '
        self.user_config = ('({})\s\((\w+)\)\s#\s'.format(self.hostname)).encode('ascii')                       # 'FortiGate (interfaces) # '

        self.regex = [self.user_login,
                      self.user_password,
                      self.user_exec,
                      self.user_config]

    def set_interface_ip(self, interface, ip, mask):
        return ['config system interface',
                'edit {}'.format(interface),
                'set mode static',
                'set ip {}/{}'.format(ip, mask),
                'end']

    def set_default_route(self, args):
        gateway, port = args[0], args[1]
        return ['config router static',
                'edit 0',
                'set device {}'.format(port),
                'set dst 0.0.0.0/0',
                'set gateway {}'.format(gateway),
                'end']

class Telnet(threading.Thread):
    def __init__(self, *args, **kwargs):
        # ip, port, hostname, end_device_type, timeout
        threading.Thread.__init__(self)
        self.output = []
        for arg in kwargs:
            if arg == 'ip':
                self.ip = kwargs[arg]
            elif arg == 'port':
                self.port = kwargs[arg]
            elif arg == 'hostname':
                self.hostname = kwargs[arg]
            elif arg == 'end_device_type':
                self.end_device_type = kwargs[arg]
            elif arg == 'timeout':
                self.timeout = kwargs[arg]

        for i, arg in enumerate(args):
            if i == 0:
                self.ip = args[i]
            elif i == 1:
                self.port = args[i]
            elif i == 2:
                self.hostname = args[i]
            elif i == 3:
                self.end_device_type = args[i]
            elif i == 4:
                self.timeout = args[i]

        if 'cisco' in self.end_device_type:
            self.device = Cisco_IOS(self.hostname)
            self.connection = TelnetLib(self.ip, self.port)

        elif 'forti' in self.end_device_type:
            self.device = FortiGate(self.hostname)
            self.connection = TelnetLib(self.ip, self.port)

        elif 'dynamips' in self.end_device_type:
            self.device = Cisco_IOS(self.hostname)
            self.netmiko_data = {
                'device_type' : 'cisco_ios_telnet',
                'host' : self.ip,
                'username' : '',
                'password' : '',
                'port' : self.port       # optional, defaults to 22
            }
            self.connect()


    def connect(self):
        if 'dynamips' in self.end_device_type:
            net_connect = ConnectHandler(**self.netmiko_data)
            self.connection = net_connect
            self.connected = True
        else:

            try:
                connection = TelnetLib(self.ip, self.port)
                self.connection = connection
                self.connected = True

            except:
                traceback_print_exc()

    def get_last_output(self, command):
        command = ((command + '\r').encode('ascii'))
        self.connection.write(command)
        #data = self.connection.read_all()
        data = self.connection.expect([self.device.eol])#, timeout=self.timeout)
        return data[2].decode('ascii')

    def run_command(self, command):
        if 'dynamips' in self.end_device_type:
            try:
                output = self.connection.send_command(command)
                return output
            except:
                traceback_print_exc()

        else:
            command = ((command + '\r').encode('ascii'))
            self.connection.write(command)
            data = self.connection.expect(self.device.regex)#, timeout=self.timeout)
            return data[2].decode('ascii')

    def run_commands(self, commands):
        for command in commands:
            data = self.run_command(command)
            self.output.append(data)

    def login(self):
        username = input('Username: ')
        password = getpass.getpass(prompt='Password: ')
        self.run_commands(['\r', username, password])

    def set_interface_ip(self, interface, ip, mask):
        if 'dynamips' in self.end_device_type:
            self.run_commands(self.device.set_interface_ip(interface, ip, mask))
        else:
            self.run_commands(self.device.set_interface_ip(interface, ip, mask))

    def set_default_route(self, *args, **kwargs):
        commands = []

        for arg in kwargs:
            if arg == 'gateway':
                commands.append(kwargs[arg])
            elif arg == 'interface':
                commands.append(kwargs[arg])

        for i, arg in enumerate(args):
            if i == 0:
                commands.append(args[i])
            elif i == 1:
                commands.append(args[i])

        self.run_commands(self.device.set_default_route(commands))


if __name__ == '__main__':
    asa = Telnet('10.255.10.30', 5018, 'ciscoasa', 'cisco_asa')
    fortigate = Telnet('10.255.10.30', 5028, 'FortiGate-VM64-KVM', 'fortigate')
    ios = Telnet('10.255.10.30', 5024, 'R1', 'dynamips')

    #fortigate.set_default_route('10.0.0.1','port1')
    #ios.set_default_route('10.0.0.1')
    #print(ios.run_command('show ip int br '))
    #time.sleep(1)
    #fortigate.login()
    #print(fortigate.run_command('show system interface'))
    #time.sleep(1)
    ios.set_interface_ip('s0/0', '10.255.30.30', '255.255.255.0')
    #asa.login()
    #print(asa.run_command('show run'))
    #print(asa.run_command('show int ip br '))
    #print(ios.run_command('show ver | inc uptime'))
    #print(ios.read_all())
    #print(fortigate.run_command('show system interface '))
