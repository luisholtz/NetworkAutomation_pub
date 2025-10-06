#Send specific commands WITH MULTITHREAD
from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
import getpass, time, os, requests
import regex as re, traceback, sys
import sharepy
import concurrent.futures
import netmiko.exceptions, paramiko.ssh_exception
import socket

#Device List
import getpass, time, os, requests
my_devs = ["9.64.24.211", "9.64.24.212"] #CHG0234272

#device_type = "cisco_ios" #juniper_junos or cisco_ios ou juniper

# Parent Directory path
parent_dir_root = r"C:\Users\lf5671\OneDrive - AT&T Services, Inc\My Documents\Customers\0.1 - IGA\IGA_US_CA_LA_Template_Updates\Change Evidences"
final_path = r"temp"
parent_dir = os.path.join(parent_dir_root, final_path)
parent_dir


#                                       
filename = "post-change"
filename = "general-commands"
#
saveOutputtoFile = 'yes' #(yes/no)

#CISCO pre-post change output commands
list_of_commands_ios = ['!-----General outputs',
                    'dir',
                    'show version',
                    'show boot system',
                    'show bootvar',
                    'show banner exec',
                    'show switch',
                    'show inventory',
                    'show stack',
                    'show power',
                    '!-----L2 feature outputs',
                    'show interface description',
                    'show interface status',
                    'show vlan brief',
                    'show cdp neighbors',
                    'show cdp neighbors detail',
                    'show lldp neighbors',
                    '!-----L3 feature outputs',
                    'show vrf',
                    'show ip bgp all summary',
                    'show ip interface brief',
                    'show ip bgp vpnv4 all ',
                    'show ip bgp vpnv6 all',
                    'show mac address-table',
                    'show ip arp',
                    'show ip arp vrf blue',
                    'show ip arp vrf 100 !SDWAN only',
                    'show ip arp vrf 210 !SDWAN only',
                    '------Ping tests',
                    'ping 8.8.8.8'
                    '!-----Current Configuration',
                    'show run']

#JUNOS pre-post change output commands
list_of_commands_junos = ['#---------------------Generic checkout commands:',
                    '#---------------------Files:',
                    'start shell',
                    'pwd',
                    'ls',
                    'exit',
                    '#---------------------General Outputs',
                    'show version | no-more',
                    'show system license',
                    'show lldp neighbors | no-more',
                    'show lldp neighbors | count',
                    'show log messages | last 150 | no-more',
                    'show chassis hardware | no-more',
                    'show virtual-chassis',
                    'show chassis fpc pic-status | no-more',
                    'show chassis routing-engine  | no-more',
                    'show system processes extensive | except 0.00% | no-more',
                    'show system alarms | no-more',
                    'show system core-dumps | no-more',
                    'show arp | no-more',
                    '#---------------------interfaces',
                    'show interfaces terse | no-more',
                    'show interfaces terse | match up | except down | match "xe|ge|ae|irb|lo|fx" | no-more',
                    'show interfaces descriptions | match up | except down | no-more',
                    'show interfaces descriptions | no-more',
                    'show interfaces terse | match up | except down | match "xe|ge|ae|irb|lo|fx" | count | no-more',
                    'show interfaces descriptions | match up | except down | count | no-more',
                    'show lacp interfaces | no-more',
                    'show lacp interfaces | match detached | no-more',
                    'show vrrp brief | no-more',
                    '#---------------------routing',
                    'show route instance extensive | no-more',
                    'show ldp neighbor | no-more',
                    'show ospf neighbor instance all | no-more',
                    'show bgp summary | no-more',
                    'show bgp summary | match establ | count',
                    'show route | match routes | no-more',
                    'show route | no-more',
                    '#---------------------BGP Advertised routes',
                    "show route advertising-protocol bgp 9.176.131.253",
                    "show route advertising-protocol bgp 9.176.131.254",
                    "show route advertising-protocol bgp 9.176.132.3",
                    "show route advertising-protocol bgp 9.176.132.4",
                    "show route advertising-protocol bgp 9.176.132.35",
                    "show route advertising-protocol bgp 9.176.132.36",
                    "show route advertising-protocol bgp 9.245.96.35",
                    "show route advertising-protocol bgp 9.245.96.36",
                    "show route advertising-protocol bgp 9.245.96.67",
                    "show route advertising-protocol bgp 9.245.96.68",
                    "show route advertising-protocol bgp 9.245.96.105",
                    "show route advertising-protocol bgp 9.245.96.106",
                    "show route advertising-protocol bgp 2620:1F7:10DA::a1b:101a",
                    "show route advertising-protocol bgp 2620:1F7:10DA::aa1:101a",
                    "show route advertising-protocol bgp 2620:1F7:10DA::b1b:101b",
                    "show route advertising-protocol bgp 2620:1F7:10DA::ba1:101b",
                    '#---------------------Ping tests',
                    'ping 8.8.8.8 count 5',
                    'ping 9.0.130.50 count 5',
                    '#---------------------Configuration Backup',
                    'show configuration | no-more',
                    'show configuration | display set | no-more']

def saveOutput(output, parent_dir, filename, hostname, ipaddr):
    if not os.path.exists(parent_dir):
        #Mkdir
        os.mkdir(parent_dir)

    #Defining file name with evidences
    logChange = f"{hostname}_{ipaddr}_{filename}.txt"
    # Path
    path = os.path.join(parent_dir, logChange)
    f = open(path, "w")
    f.write(output)
    f.close()

def send_commands(device_ip):
        try:
            #Detecting device_type automatically
            Detect_device = {'device_type': 'autodetect',
                             'host': device_ip,
                             'username': UserGtac,
                             'password': passwdUserGtac,
                             'secret': passwdUserGtac
                             }
            guesser = SSHDetect(**Detect_device)
            while guesser is None:
                guesser = SSHDetect(**Detect_device)
            device_type = guesser.autodetect()
            #End of detecting device_type automatically

            if device_type == 'cisco_ios':
                list_of_commands = list_of_commands_ios
            if device_type == 'juniper_junos':
                    list_of_commands = list_of_commands_junos
        
            start = time.perf_counter()
            #passwd = passwdUserGtac #getpass.getpass('Please enter the password: ')
            device = {
                "device_type": device_type,
                "host": device_ip,
                "username": UserGtac,
                "password": passwdUserGtac, # Log in password from getpass
                "secret": passwdUserGtac, # Enable password from getpass
                "session_log": r'C:\temp\netmiko_session_'+device_ip+'_log.txt',
                "fast_cli": False
            }
            connection = ConnectHandler(**device)
            connection.enable()
            hostname = connection.find_prompt().rstrip(">").rstrip("#").rstrip(">t")
            if hostname:
                print(f'Device {hostname} - {device["host"]} is reachable')
            else:
                print(f'Device {hostname} - {device["host"]} is not reachable')
            output = "List of extracted commands from device"
            output += "\n"+120*'-'+'\n'
            #Print list of commands spliting lines
            output += '\n'.join(list_of_commands)
            output += "\n"+120*'-'+'\n'
            output += connection.send_multiline_timing(list_of_commands, read_timeout=0)
            output += "\n"+120*'-'
            #print(f'Connected to {hostname} - {device["host"]}')
            #print(output)
            connection.disconnect()
            #print(f'Closing Connection on {hostname} - {device["host"]}')
            finish = time.perf_counter()
            #print(f'Finished in {round(finish-start, 2)} second(s)')
            #print(120*'-')

            #Save Output function
            if saveOutputtoFile == 'yes':
                saveOutput(output, parent_dir, filename, hostname, device_ip)
            return output

        except (netmiko.exceptions.NetmikoTimeoutException, 
                netmiko.exceptions.NetmikoAuthenticationException, 
                netmiko.exceptions.ReadTimeout) as e:
            print(e)
            print(type(e))
            traceback.print_exc(file=sys.stdout)
            pass
        except Exception as e:
            print(e)
            print(type(e))
            traceback.print_exc(file=sys.stdout)
            pass

try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        #results = [executor.submit(send_commands_ios, device_ip) for device_ip in my_devs]
        results = executor.map(send_commands, my_devs)

        for result in results:
             print(result)
        '''for f in concurrent.futures.as_completed(results):
             print(f.result())'''
        
except Exception as e:
    print(e)
    print(type(e))
    traceback.print_exc(file=sys.stdout)
