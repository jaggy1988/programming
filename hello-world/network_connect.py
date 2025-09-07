import paramiko
from netmiko import ConnectHandler
import re
from device_info import ios_xe1 as device



print ("Start of the program")
# Hostname function
def My_function (Output_Str):
    put_Str = Output_Str.rstrip("#")
    return put_Str

# Create a CLI command template
show_interface_config_temp = "show running-config interface {}"

# Open CLI connection to device
with ConnectHandler(ip = device["address"],
                    port = device["ssh_port"],
                    username = device["username"],
                    password = device["password"],
                    device_type = device["device_type"]) as ch:

# Create desired CLI command and send to device
   command = show_interface_config_temp.format("Loopback 1234")
   interface = ch.send_command(command)

# Print the raw command output to the screen
print(interface)


Hostname = "Jagatheesh#"
Print_Str = My_function(Hostname)
print (Print_Str)
print ("End of the program")