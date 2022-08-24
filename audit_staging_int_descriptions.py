# Python script utilizing PyATS and Nornir3 to audit Cisco IOS-XR Interface descriptions.
# Find and fix leftover "Staging" keywords on up/up interfaces, 
# which prevent them from being monitored by the NOC. 

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result

import pprint
pp = pprint.PrettyPrinter(indent=4)

from genie.testbed import load
tb = load('yaml/lab_devices.yaml')


try:

    # For each router in the testbed file, connect to it and run "show interfaces descriptions", storing the output in a dictionary
    for name, dev in tb.devices.items():
        # Initial Vars
        show_int_desc = {}
        
        #Connect to the router
        dev.connect(init_exec_commands=[], init_config_commands=[])

        # Show int description command sent, returns Dictionary
        show_int_desc[name] = dev.parse('show interfaces description')

        # For every interface in the output of "show int description" from this router
        for interface in show_int_desc[name]["interfaces"]:

            # If the interface is "Up"
            if show_int_desc[name]["interfaces"][interface]["status"] == "up":

                # If the interface has the string "Staging:" in it, then record that interface for us to inspect
                if "Staging:" in str(show_int_desc[name]["interfaces"][interface]["description"]):

                    #print(interface + " has interface description " + str(show_int_desc[name]["interfaces"][interface]["description"]) + " and is Status is Up")
                    description = str(show_int_desc[name]["interfaces"][interface]["description"])
                    description = description.strip("Staging: ")

                    nornir = InitNornir('yaml/config.yml')

                    description_config = [
                        "interface " + interface,
                        f"description {description}",
                        "commit"
                    ]
                    
                    result = nornir.run(netmiko_send_config, config_commands=description_config)
                    print_result(result)

                    
except Exception as e:
    print(e)
