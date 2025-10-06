#Starts creating template update based on CTR process WITH MULTITHREAD
#This automation login in each device listed in "my_devices" and colect some command outputs "list_of_commands", running-config and so on. Besides it detects 
# the used template name in the configuration file to download it automatically from att sharepoint and place all these files into a directory named with the dev hostname.
#It was firstly designed to vUA switches
#It works with vSA switches as well March/03/2023
#Implemented to any cisco device and Junos Nov/01/2023

from netmiko import ConnectHandler
from netmiko.ssh_autodetect import SSHDetect
import getpass, time, os, requests
import regex as re, traceback, sys
import sharepy
import concurrent.futures
import netmiko.exceptions
import paramiko.ssh_exception
import os
import tempfile
import office365
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

parent_dir = r"C:\Users\lf5671\OneDrive - AT&T Services, Inc\My Documents\Customers\0.1 - IGA\IGA_US_CA_LA_Template_Updates\_In Preparation"


#CISCO pre-post change output commands
list_of_commands_cisco = ['!-----General outputs',
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
                    'show ip route',
                    'show ip route vrf blue',
                    'show ip bgp all summary',
                    'show ip interface brief',
                    'show ip bgp vpnv4 all ',
                    'show ip bgp vpnv6 all',
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
                    '#---------------------General Output',
                    'show version | no-more',
                    'show lldp neighbors | no-more',
                    'show lldp neighbors | count',
                    'show log messages | last 100 | no-more',
                    'show chassis hardware | no-more',
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
                    'show ldp neighbor | no-more',
                    'show ospf neighbor instance all | no-more',
                    'show bgp summary | no-more',
                    'show bgp summary | match establ | count',
                    'show route | match routes | no-more',
                    'show route | no-more',
                    '#---------------------Ping tests',
                    'ping 8.8.8.8 count 5',
                    '#---------------------Configuration Backup',
                    'show configuration | no-more']

def saveOutput(output, parent_dir, filename, hostname, device_ip, device_type):
    if not os.path.exists(parent_dir):
        #Mkdir
        os.mkdir(parent_dir)

    hostDir=f"{parent_dir}\{hostname}_{device_ip}_{device_type}"
    if not os.path.exists(hostDir):
        #Mkdir
        os.mkdir(hostDir)

    #Defining file name
    fileName = f"{hostname}_{filename}.txt"
    # Path
    path = os.path.join(hostDir, fileName)
    f = open(path, "w")
    f.write(output)
    f.close()

def CTR_SCRIPT_PROCESS(device_ip):
    #passwd = passwdUserGtac #getpass.getpass('Please enter the password: ')
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
    device = {
        "device_type": device_type,
        "host": device_ip,
        "username": UserGtac,
        "password": passwdUserGtac, # Log in password from getpass
        "secret": passwdUserGtac # Enable password from getpass
    }

    connection = ConnectHandler(**device)
    connection.enable()
    hostname = connection.find_prompt().rstrip(">").rstrip("#").rstrip(">t")
    print(f'Connected to {hostname} - {device["host"]}')
    output = "List of extracted commands from device"
    output += "\n"+120*'-'+'\n'
    if device_type == "cisco_ios":
        list_of_commands = list_of_commands_cisco
        showRun = connection.send_command_timing("show run", read_timeout=0)
    if device_type == "juniper_junos":
        list_of_commands = list_of_commands_junos
        showRun = connection.send_command_timing("show configuration | no-more", read_timeout=0)
    #Print list of commands spliting lines
    output += '\n'.join(list_of_commands)
    output += "\n"+120*'-'+'\n'
    output += connection.send_multiline_timing(list_of_commands, read_timeout=0)
    connection.disconnect()

    commandsFile = f"PRE_COMMANDS"
    showRunFile = f"CONFIG_BKP"
    #Finding template name with RegEx
    templateName = re.search(r"(\/\s)([a-zA-Z].*)(\.txt)", output)
    templateName = templateName.group(2)#+'-kyn'
    templateFile = f"{parent_dir}\{hostname}_{device_ip}_{device_type}\{templateName}_TEMPLATE.txt"

    #Saving ouput
    print("% s' --> saving..." % commandsFile)
    saveOutput(output, parent_dir, commandsFile, hostname, device_ip, device_type)
    
    #Saving showRun
    print("% s' --> saving..." % showRunFile)
    saveOutput(showRun, parent_dir, showRunFile, hostname, device_ip, device_type)

    #Template download Searching for the right Customer
    customer = re.search(r'(\-kyn)', templateName)
    if customer is None:
        #https://att.sharepoint.com/sites/NetArch/sharepoint/netopt/current/vUA-3650d.txt  ***** vUA dafault path
        templateUrl = f"https://att.sharepoint.com/sites/NetArch/sharepoint/netopt/current/{templateName}.txt"
    else:
        #templateUrl = f"https://att.sharepoint.com/sites/NetArch/sharepoint/kyndryl/current/{templateName}.txt"#Kyndryl
        templateUrl = f"https://att.sharepoint.com/sites/NetArch/sharepoint/kyndryl/current/{templateName}.txt"
    print("% s' --> downloading..." % templateUrl)
    """
    #sharepy Stoped working for some unknown reason 
    s = sharepy.connect("https://att.sharepoint.com", username=UserAttGlobalLogon, password=passwdAttGlobalLogon)
    #s = sharepy.connect("https://att.sharepoint.com", None, None)
    """
    #Testing another method to download sharepoint content into a file because user and password is deprecated
    """
    Demonstrates how to download a file from SharePoint site
    """
    ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
    file_url = "Shared Documents/big_buck_bunny.mp4"
    # file_url = "Shared Documents/!2022/Financial Sample.xlsx"
    download_path = os.path.join(tempfile.mkdtemp(), os.path.basename(file_url))
    with open(download_path, "wb") as local_file:
        file = (
            ctx.web.get_file_by_server_relative_url(file_url)
            .download(local_file)
            .execute_query()
        )
    print("[Ok] file has been downloaded into: {0}".format(download_path))

    r = s.getfile(templateUrl, filename=templateFile)
    
    print(f'Closing Connection on {hostname} - {device["host"]}')
    print(120*'-')
    return

try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = [executor.submit(CTR_SCRIPT_PROCESS, device_ip) for device_ip in my_devs]

        for f in concurrent.futures.as_completed(results):
             print(f.result())
    
except (netmiko.exceptions.NetmikoAuthenticationException, 
        paramiko.ssh_exception.AuthenticationException, 
        netmiko.exceptions.NetmikoTimeoutException) as e:
    print(e)
    #print(type(e))
    #traceback.print_exc(file=sys.stdout)
    pass

except Exception as e:
    print(e)
    print(type(e))
    traceback.print_exc(file=sys.stdout)
