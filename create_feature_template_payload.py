import requests
import sys
import json
import os
import socket
import subprocess
import time


vedge_model_list = ["vedge-1000","vedge-2000","vedge-cloud","vedge-5000","vedge-ISR1100-6G","vedge-100-B","vedge-ISR1100-4G","vedge-ISR1100-4GLTE","vedge-100-M"]
cedge_model_list = [
"vedge-CSR-1000v",
"vedge-IR-1101",
"vedge-ISR-4331",
"vedge-ISR-4321",
"vedge-ISR-4351",
"vedge-ISR-4221",
"vedge-ISR-4221X",
"vedge-ISR-4431",
"vedge-ISR-4461",
"vedge-ISR-4451-X",
"vedge-ASR-1001-HX",
"vedge-ASR-1002-X",
"vedge-ASR-1002-HX",
"vedge-C1111-8P",
"vedge-C1111X-8P",
"vedge-C1111-8PLTEEA",
"vedge-C1111-8PLTELA",
"vedge-C1117-4PLTEEA",
"vedge-C1127X-8PMLTEP",
"vedge-C1117-4PLTELA",
"vedge-ISRv",
"vedge-ASR-1001-X",
"vedge-nfvis-CSP2100",
"vedge-nfvis-CSP2100-X1",
"vedge-nfvis-CSP2100-X2",
"vedge-nfvis-UCSC-C",
"vedge-nfvis-UCSC-E",
"vedge-C1101-4P",
"vedge-C1101-4PLTEP",
"vedge-C1111-4P",
"vedge-C1111-8PW",
"vedge-C1111-8PLTEEAW",
"vedge-C1111-4PLTEEA",
"vedge-C1111-4PLTELA",
"vedge-C1116-4P",
"vedge-C1116-4PLTEEA",
"vedge-C1117-4P",
"vedge-C1117-4PM",
"vedge-C1117-4PMLTEEA",
"vedge-C1161X-8P",
"vedge-C1101-4PLTEP",
"vedge-C1127X-8PMLTEP",
"vedge-C1121-8PLTEPW",
"vedge-C1111-8PLTELAW",
"vedge-C1126X-8PLTEP",
"vedge-C1127X-8PLTEP",
"vedge-C1101-4PLTEPW",
"vedge-C1109-4PLTE2PW",
"vedge-C1109-4PLTE2P",
"vedge-C1121X-8PLTEP",
"vedge-C1161X-8PLTEP",
"vedge-C1113-8PMLTEEA",
"vedge-C1121X-8P"
]



default_template_payload = {
    "templateName": "test_vpn_19_API",
    "templateDescription": "test_vpn_19_API",
    "templateType": "vpn-vedge",
    "deviceType": [
        "vedge-1000",
    ],
    "factoryDefault": 'false',
    "templateMinVersion": "15.0.0",
}

def create_omp_payload(site,device_list):
    omp_definition_default = open("./default_template/Factory_Default_vEdge_OMP_Template.json", "r")
    omp_definition_default_json = json.load(omp_definition_default)
    omp_definition = omp_definition_default_json
    omp_template_payload = default_template_payload
    omp_template_payload['deviceType'] = device_list
    omp_template_payload['templateName'] = site + "_OMP_Template"
    omp_template_payload['templateDescription'] = site + "_OMP_Template_API"
    omp_template_payload['templateType'] = "omp-vedge"
    omp_template_payload['templateDefinition']= omp_definition
    return omp_template_payload


def create_bfd_payload(site,device_list):
    bfd_definition_default = open("./default_template/Factory_Default_BFD_Template.json", "r")
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
    bfd_template_payload['templateType'] = "bfd-vedge"
    bfd_template_payload['templateDefinition']= bfd_definition
    return (bfd_template_payload)



def create_vpn_payload(site,device_type,vpn ='0',vpn_routes =0):
    vpn_template_payload = default_template_payload
    vpn_template_payload['templateName'] = site + "_VPN_" + vpn + "_Template"
    vpn_template_payload['templateDescription'] = site + "_VPN_" + vpn + "_Template_API"
    vpn_template_payload['templateType'] = "vpn-vedge"
    vpn_template_payload['deviceType'] = [""]
    vpn_template_payload['deviceType'][0] = device_type
    
    vpn_definition_default = open("./default_template/Factory_Default_vEdge_VPN_0_Template.json", "r")
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
                    "vipVariableName":"vpn_next_hop_ip_address_" + str(x)
                    },
                "distance":{
                    "vipObjectType":"object",
                    "vipType":"ignore",
                    "vipValue":1,
                    "vipVariableName":"vpn_next_hop_ip_distance_"+ str(x)
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
                        "priority-order": ["prefix","next-hop"]
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
    

    return (vpn_template_payload)
    #print(json.dumps(vpn_template_payload,indent=2))
    #print(vpn_template_payload)





def create_int_payload(site,device_type,ifname = '', ip = 'dhcp',tunnel = 'false',nat = 'false',mgmt='false',restrict = 'false'):
    int_definition_default = open("./default_template/Factory_Default_vEdge_DHCP_Tunnel_Interface.json", "r")
    int_definition_default_json = json.load(int_definition_default)
    int_definition = int_definition_default_json
    int_template_payload = default_template_payload
    int_template_payload['deviceType'] = [""]
    int_template_payload['deviceType'][0] = device_type

    if tunnel == 'true':
        int_template_payload['templateName'] = site+"_WAN_"+ifname
        int_template_payload['templateDescription'] = site+"_WAN_"+ifname.replace('/','_')+"_API"
        int_template_payload['templateDescription'] = int_template_payload['templateDescription'].replace('.','_')
        int_template_payload['templateType'] = "vpn-vedge-interface"
       
        #Interface Properties
        int_definition['if-name']["vipType"] = "constant"
        int_definition['if-name']["vipValue"] = ifname
        int_definition["description"]["vipType"] = "constant"
        int_definition["description"]["vipValue"] = "WAN_Interface"

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
                    "vipVariableName": "WAN_"+ifname.replace('/','')
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
    else:
        # LAN ## 
        int_template_payload['templateType'] = "vpn-vedge-interface"
        int_template_payload['templateName'] = site+"_LAN_"+ifname
        int_template_payload['templateDescription'] = site+"_LAN_"+ifname.replace('/','_')+"_API"
        int_template_payload['templateDescription'] = int_template_payload['templateDescription'].replace('.','_')
        int_definition["description"]["vipValue"] = "LAN_Interface"
        int_definition["description"]["vipType"] = "constant"
        int_definition['if-name']["vipType"] = "constant"
        int_definition['if-name']["vipValue"] = ifname

        # Check the interface is a management interface or not
        if mgmt == 'true': 
            int_template_payload['templateName'] = site+"_MGT_"+ifname
            int_template_payload['templateDescription'] = site+"_MGT_"+ifname.replace('/','_')+"_API"
            int_template_payload['templateDescription'] = int_template_payload['templateDescription'].replace('.','_')
            int_definition["description"]["vipValue"] = "MGT_Interface"
            int_definition["shutdown"]['vipValue'] = 'true'
        
        
        #Remove Tunnel-interface
        del int_definition['tunnel-interface']
    if "." in ifname :
        int_definition['mtu'] = {
            "vipObjectType": "object",
            "vipType": "constant",
            "vipValue": 1500
        }
    if ip == 'static':
        int_definition['ip'] = {
            "address": {
                "vipObjectType": "object",
                "vipType": "variableName",
                "vipValue": "",
                #"vipVariableName": "WAN_"+ifname.replace('/','')                
                "vipVariableName": int_definition["description"]["vipValue"][0:3]+"_"+ifname.replace('/','_')
            }
        }
    if ip == 'null':
        int_template_payload['templateName'] = site+"_Parent_"+ifname
        int_template_payload['templateDescription'] = site+"_Parant_"+ifname.replace('/','_')+"_API"
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
                    "bandwidthPercent":"70",
                    "bufferPercent":"70",
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
                },
            "isPolicyActivated":"false"
            }
    }
    return(localized_policy_payload)

