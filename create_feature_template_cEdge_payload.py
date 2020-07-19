import requests
import sys
import json
import os
import socket
import subprocess
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


default_template_payload = {
    "templateName": "test_vpn_19_API",
    "templateDescription": "test_vpn_19_API",
    "templateType": "vpn-vedge",
    "deviceType": [
        "vedge-ASR-1001-X",
    ],
    "factoryDefault": 'false',
    "templateMinVersion": "15.0.0",
}

def create_omp_cEdge_payload(site,device_list):
    omp_definition_default = open("./default_template_cEdge/Factory_Default_Cisco_OMP_ipv46_Template.json", "r")
    omp_definition_default_json = json.load(omp_definition_default)
    omp_definition = omp_definition_default_json
    omp_template_payload = default_template_payload
    omp_template_payload['deviceType'] = device_list
    omp_template_payload['templateName'] = site + "_OMP_Template"
    omp_template_payload['templateDescription'] = site + "_OMP_Template_API"
    omp_template_payload['templateType'] = "cisco_omp"
    omp_template_payload['templateDefinition']= omp_definition
    return omp_template_payload


def create_bfd_cEdge_payload(site,device_list):
    bfd_definition_default = open("./default_template_cEdge/Factory_Default_Cisco_BFD_Template.json", "r")
    bfd_definition_default_json = json.load(bfd_definition_default)
    bfd_definition = bfd_definition_default_json
    bfd_definition['app-route'] = {
        "multiplier": {
            "vipObjectType": "object",
            "vipType": "ignore",
            "vipValue": 6,
            "vipVariableName": "bfd_multiplier"
            },
        "poll-interval": {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": 5000,
            "vipVariableName": "bfd_poll_interval"
            }
    }

    bfd_template_payload = default_template_payload
    bfd_template_payload['deviceType'] = device_list
    bfd_template_payload['templateName'] = site + "_BFD_Template"
    bfd_template_payload['templateDescription'] = "_BFD_Template"
    bfd_template_payload['templateType'] = "cisco_bfd"
    bfd_template_payload['templateDefinition']= bfd_definition
    return (bfd_template_payload)



def create_vpn_cEdge_payload(site,device,vpn ='0',vpn_routes =0):
    vpn_template_payload = default_template_payload
    vpn_template_payload['deviceType'] = [""]
    vpn_template_payload['templateName'] = site + "_VPN_" + vpn + "_Template"
    vpn_template_payload['templateDescription'] = site + "_VPN_" + vpn + "_Template_api"
    vpn_template_payload['templateType'] = "cisco_vpn"
    vpn_template_payload['deviceType'][0] = device
    
    vpn_definition_default = open("./default_template_cEdge/Factory_Default_Cisco_VPN_0_Template.json", "r")
    vpn_definition_default_json = json.load(vpn_definition_default)
    wan_vpn_definition = vpn_definition_default_json
    vpn_routes = int(vpn_routes)


    if vpn_routes > 0 : 
        next_hop_routes_payload= [0] *vpn_routes
        for x in range(0,vpn_routes) : 
            #print(x)
            next_hop_routes_payload[x] = {
                "address":{
                    "vipObjectType":"object",
                    "vipType":"variableName",
                    "vipValue":"",
                    "vipVariableName":"vpn_"+vpn+"_next_hop_ip_address_" + str(x)
                    },
                "distance":{
                    "vipObjectType":"object",
                    "vipType":"ignore",
                    "vipValue":1,
                    "vipVariableName":"vpn_"+vpn+"_next_hop_ip_distance_"+ str(x)
                },
                "priority-order":["address","distance"]
            }

    # Building VPN_Definition "ip" Payload   
        wan_vpn_ip = {
            "route":{
                "vipType":"constant",
                "vipValue":[
                    {
                        "prefix":{
                            "vipType":"constant",
                            "vipObjectType":"Object",
                            "vipValue":"0.0.0.0/0",
                            "vipVariableName": "vpn_ipv4_ip_prefix"
                        },
                        "next-hop":{
                            "vipType":"constant",
                            "vipValue":[],
                            "vipObjectType":"tree",
                            "vipPrimaryKey":["address"]  
                        },
                        "priority-order": ["prefix","next-hop","null0","distance","vpn"]
                    }
                ],
                "vipObjectType": "tree",
                "vipPrimaryKey": [
                    "prefix"
                    ]
                },
            }   
    
    #print(len(next_hop_routes_payload))
    if vpn_routes > 0:
        for x in range(0,len(next_hop_routes_payload)):
            wan_vpn_ip['route']['vipValue'][0]['next-hop']['vipValue'].append(next_hop_routes_payload[x])
        wan_vpn_definition['ip'] = wan_vpn_ip
    
    wan_vpn_definition['vpn-id']['vipType'] = "constant"
    wan_vpn_definition['vpn-id']['vipValue'] = int(vpn)
    #print(wan_vpn_definition['vpn-id'])
    vpn_template_payload["templateDefinition"] = wan_vpn_definition
    #print(json.dumps(vpn_template_payload))

    return (vpn_template_payload)
    #print(json.dumps(vpn_template_payload,indent=2))
    #print(vpn_template_payload)



def create_int_cEdge_payload(site,device,ifname = '', ip = 'dhcp',tunnel = 'false',nat = 'false',mgmt='false',restrict = "false"):
    int_definition_default = open("./default_template_cEdge/Factory_Default_Cisco_DHCP_Tunnel_Interface.json", "r")
    int_definition_default_json = json.load(int_definition_default)
    int_definition = int_definition_default_json
    int_template_payload = default_template_payload
    int_template_payload['deviceType'] = [""]
    int_template_payload['deviceType'][0] = device
    
    if tunnel == 'true':
        int_template_payload['templateName'] = site+"_WAN_"+ifname
        int_template_payload['templateDescription'] = site+"_WAN_"+ifname+"_API"
        int_template_payload['templateType'] = "cisco_vpn_interface"
       
        #Interface Properties
        int_definition['if-name']["vipType"] = "constant"
        int_definition['if-name']["vipValue"] = ifname
        int_definition["description"]["vipType"] = "constant"
        int_definition["description"]["vipValue"] = "WAN_"

        int_definition['tunnel-interface'] = {
            "encapsulation":{
                "vipType": "constant",
                "vipValue": [
                    {
                        "preference": {
                            "vipObjectType": "object",
                            "vipType": "ignore",
                            "vipVariableName": "vpn_if_tunnel_ipsec_preference"
                        },
                        "weight": {
                            "vipObjectType": "object",
                            "vipType": "ignore",
                            "vipValue": '1',
                            "vipVariableName": "vpn_if_tunnel_ipsec_weight"
                        },
                        "encap":{
                            "vipType":"constant",
                            "vipValue": "ipsec",
                            "vipObjectType" : "object"
                        },
                        "priority-order":[
                            "encap",
                            "preference",
                            "weight"
                        ]
                    }
                ],
                "vipObjectType": "tree",
                "vipPrimaryKey": ["encap"]
            },
            "color": {
                "value": {
                    "vipObjectType": "object",
                    "vipType": "variableName",
                    "vipValue": "",
                    "vipVariableName": "WAN_"+ifname.replace('/','_')
                    },
                "restrict": {
                    "vipObjectType": "node-only",
                    "vipType": "ignore",
                    "vipValue": "false",
                    "vipVariableName": "vpn_if_tunnel_color_restrict"
                    }
                },
            "allow-service": {
                "all": {
                    "vipObjectType": "object",
                    "vipType": "constant",
                    "vipValue": "true",
                    "vipVariableName": "vpn_if_tunnel_all"
                    }
                }
            }
        if restrict == 'true' : 
            int_definition['tunnel-interface']["color"]['restrict']['vipType'] = 'constant'
            int_definition['tunnel-interface']["color"]['restrict']['vipValue'] = 'true'

    elif tunnel == 'false' and mgmt != 'true':
        int_template_payload['templateName'] = site+"_LAN_"+ifname
        int_template_payload['templateDescription'] = site+"_LAN_"+ifname+"_API"
        int_template_payload['templateType'] = "cisco_vpn_interface"

        #Interface Properties
        int_definition['if-name']["vipType"] = "constant"
        int_definition['if-name']["vipValue"] = ifname
        int_definition["description"]["vipType"] = "constant"
        int_definition["description"]["vipValue"] = "LAN"
        
        #Remove Tunnel-interface
        del int_definition['tunnel-interface']
    
    elif tunnel == 'false' and mgmt == 'true':
        int_template_payload['templateName'] = site+"_MGMT_"+ifname
        int_template_payload['templateDescription'] = site+"_MGMT_"+ifname+"_API"
        int_template_payload['templateType'] = "cisco_vpn_interface"

        #Interface Properties
        int_definition['if-name']["vipType"] = "constant"
        int_definition['if-name']["vipValue"] = ifname
        int_definition["description"]["vipType"] = "constant"
        int_definition["description"]["vipValue"] = "MGMT_Interface"
        
        #Remove Tunnel-interface
        del int_definition['tunnel-interface']
    
    if "." in ifname :
        int_definition['mtu'] = {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": 1500
        }

    if ip == 'null':
        int_template_payload['templateName'] = site+"_Parent_"+ifname
        int_template_payload['templateDescription'] = site+"_Parant_"+ifname+"_API"
        int_template_payload['templateDescription'] = int_template_payload['templateDescription'].replace('.','_')
        int_definition["description"]["vipValue"] = "Parent_Interface"
        int_definition["description"]["vipType"] = "constant"
        int_definition['mtu'] = {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": 1504
        }
        int_definition['ip'] = {
            "address": {
                "vipObjectType": "object",
                "vipType": "ignore",
                "vipVariableName": "vpn_if_ipv4_address"
            }
        }   

    if ip == 'static':
        int_definition['ip'] = {
            "address": {
                "vipObjectType": "object",
                "vipType": "variableName",
                "vipValue": "",
                "vipVariableName": "WAN_"+ifname.replace('/','_')
            }
        }
    if nat == 'true' :
        int_definition['nat']={
            "block-icmp-error": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": "false",
                "vipVariableName": "nat_block_icmp_error"
                },
            "respond-to-ping": {
                "vipObjectType": "object",
                "vipType": "constant",
                "vipValue": "true",
                "vipVariableName": "nat_respond_to_ping"
                }           
        }
    
    int_template_payload["templateDefinition"] = int_definition
    #print (json.dumps(int_template_payload))
    return (int_template_payload)

def create_class_map_list_payload(queue):
    queue = int(queue)
    class_map_payload = [0]*queue
    for x in range(0,queue):
        class_map_payload[x] = {
           "name":"Queue"+str(x+1),
            "description":"Desc Not Required",
            "type":"class",
            "entries":[
                {
                    "queue": str(x+1)
                }
            ] 
        }
    return(class_map_payload)  

def create_qos_map_payload(qos_ref):
    #qos_ref = query list of class-map from list localized policy
    #Request URL: https://vmanage-1629537.viptela.net/dataservice/template/policy/list/class

    qos_payload = {
        "name":"qos_map",
        "type":"qosMap",
        "description":"qos_map_api",
        "definition":
            {
            "qosSchedulers":
                [
                {
                    "queue":"0",
                    "bandwidthPercent":"63",
                    "bufferPercent":"63",
                    "burst":"15000",
                    "scheduling":"llq",
                    "drops":"tail-drop",
                    "classMapRef":""
                }
            ]
            }
        }
    
    for x in qos_ref :
        
        queue = {
            "queue":x["entries"][0]["queue"],
                    "bandwidthPercent":"10",
                    "bufferPercent":"10",
                    "scheduling":"wrr",
                    "drops":"red-drop",
                    "classMapRef": x["listId"] 
        }        
        qos_payload["definition"]["qosSchedulers"].append(queue)
    
    qos_payload["definition"]["qosSchedulers"][0]["bandwidthPercent"] = str(100 -(len(qos_ref))*10)
    qos_payload["definition"]["qosSchedulers"][0]["bufferPercent"] = str(100 -(len(qos_ref))*10)
    return(qos_payload)
    


def create_localized_policy_payload(qos_map_id):
    localized_policy_payload  = {
        "policyDescription":"localized_policy",
        "policyType":"feature",
        "policyName":"localized-policy",
        "policyDefinition":
            {
            "assembly":[
                {"definitionId":qos_map_id,"type":"qosMap"}
            ],
            "settings":
                {
                    "appVisibility":"true",
                    "flowVisibility":"true",
                    "cloudQos":"true"
                }
            },
        "isPolicyActivated":"false"
    }
    return(localized_policy_payload)

