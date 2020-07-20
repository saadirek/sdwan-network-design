# sdwan-network-design
## Objectives
Automatic creating the Feature Templates on vManage from the netowrk design config file.

## Requirements
To use this code you will need:

Python 3.7+
Cisco SDWAN vManage 20.1+
Supported : vEdge, cEdge 

Feature template supported 
- OMP 
- BFD 
- VPN 
- Interface Tunnel / Tunnel restriction
- Sub-interface.
- Localized-Policy
 
For subinterface, the user does not need to put in the "Parent" interface. The user just put in the sub-interface eg. "GigabitEthernet0/0/1.100". Script will automatically create the parent interface with the 1504 MTU size. 

## Install and Setup 
Download the code to local machine 
```
git clone https://github.com/saadirek/sdwan-network-design.git
cd sdwan-network-design
```
Setup virtual environment
```
python3.7 -m venv venv
source venv/bin/activate
pip install requirements.txt
```
Before running the script, the config.json file needs to be modified first. The example of the config file is at the ./config/config.json. The user needs to go there and edit the information of the prefix, wan, lan and so on. When editting, please follow the format strictly. Eg. all boolean infomation will be put as a string. ("true","false"). 

For the model, the user can see it in the "model_list.txt". Please put the exact name in the model field.

Example of the config.json 
```
{
    "edge_router": [
        {
            "prefix" : "HQ",
            "model" : "vedge-ISR-4331",
            "wan_route": "2",
            "interface" : {
            "wan": [
                {
                    "if_name" : "GigabitEthernet0/0/0",
                    "ip_type" : "dhcp",
                    "nat_type" : "true",
                    "restrict" : "true"
                },
                {
                    "if_name" : "GigabitEthernet0/0/1",
                    "ip_type" : "static",
                    "nat_type" : "false",
                    "restrict" : "true"
                }
            ],
            "lan": [
                {
                    "if_name" : "GigabitEthernet0/0/2",
                    "ip_type" : "static"
                }
            ],
            "mgmt": [
                {
                    "oob_mgmt" : "true",
                    "if_name" : "GigabitEthernet0"
                }
            ]
            }
        }
    ],  
    "global_qos" : "true",
    "global_omp":"true",
    "global_bfd":"true"
}

```
The user can also edit the global feature template and localized policy. If "true", the script will configure for both vEdge and cEdge IOS-XE SDWAN. Note, the global_qos should set as "false" if the script is run for the 2nd time. Otherwise, it will throw the error configuring the qos because the qos configuration is already pushed to the vManage. But it should be fine.

Once edited, Go back to sdwan-network-design directory and run the code.
```
python network-design-config.py <VMANAGE_IP_ADDRESS> <USER> <PASSWORD> 
```

## Note : 
When using this script. Please do not remove any other folders in the repository.
