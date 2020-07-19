
import requests
import sys
import json
import os
import socket
import subprocess
from create_feature_template_payload import *
from create_feature_template_cEdge_payload import *
import urllib.request 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SDWAN_IP = sys.argv[1]
SDWAN_USERNAME = sys.argv[2]
SDWAN_PASSWORD = sys.argv[3]


class rest_api_lib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = vmanage_ip
        self.session = {}
        self.login(self.vmanage_ip, username, password)

    def login(self, vmanage_ip, username, password):
        """Login to vmanage"""
        base_url_str = 'https://%s:443/'%vmanage_ip

        login_action = '/j_security_check'

        #Format data for loginForm
        login_data = {'j_username' : username, 'j_password' : password}

        #Url for posting login data
        login_url = base_url_str + login_action
        url = base_url_str + login_url


        #URL for retrieving client token
        token_url = base_url_str + 'dataservice/client/token'

        sess = requests.session()
        #If the vmanage has a certificate signed by a trusted authority change verify to True
        login_response = sess.post(url=login_url, data=login_data, verify=False)



        if b'<html>' in login_response.content:
            print ("Login Failed")
            sys.exit(0)

        login_token = sess.get(url=token_url, verify=False)
        if b'<html>' in login_token.content:
            print ("Login Token Failed")
            exit(0)

        #update token to session headers
        sess.headers['X-XSRF-TOKEN'] = login_token.content
        # print(login_token.content)
        self.session[vmanage_ip] = sess

    def get_request(self, mount_point,headers={'Content-Type': 'application/json'}):
        """GET request"""
        url = "https://%s:443/dataservice/%s"%(self.vmanage_ip, mount_point)
        #print url
        response = self.session[self.vmanage_ip].get(url=url,headers = headers,  verify=False)
        data = response.content
        return data

    def post_request(self, mount_point, payload, headers={'Content-Type': 'application/json'}):
        """POST request"""
        url = "https://%s:443/dataservice/%s"%(self.vmanage_ip, mount_point)
        payload = json.dumps(payload)
        #print (payload)
        params = {'confirm':'true'}
        response = self.session[self.vmanage_ip].post(url=url, data=payload, params = params,headers=headers, verify=False)
        data = response.content
        
        return data

    def put_request(self, mount_point, payload,headers={'Content-Type' : 'application/json'}):
        """POST request"""
        url = "https://%s:443/dataservice/%s"%(self.vmanage_ip, mount_point)
        # payload = json.dumps(payload)
        #print (payload)

        response = self.session[self.vmanage_ip].put(url=url, data=payload,headers=headers,verify=False)
        # print(response.status_code)
        # data = response.json()
        # return data


sdwanp = rest_api_lib(SDWAN_IP, SDWAN_USERNAME, SDWAN_PASSWORD)

feature_templates = sdwanp.get_request('template/feature')
feature_templates = json.loads(feature_templates)

template_collection = [
    "Factory_Default_vEdge_DHCP_Tunnel_Interface",
    "Factory_Default_vEdge_VPN_0_Template",
    "Factory_Default_vEdge_OMP_Template",
    "Factory_Default_BFD_Template",
    "Factory_Default_Logging_Template"
]

template_collection_cEdge = [
    "Factory_Default_Cisco_DHCP_Tunnel_Interface",
    "Factory_Default_Cisco_VPN_0_Template",
    "Factory_Default_Cisco_OMP_ipv46_Template",
    "Factory_Default_Cisco_BFD_Template",
    "Factory_Default_Cisco_Logging_Template"
]
template_collection_json = []
template_collection_cEdge_json = []


#Extracting the Default Template from vManage 

for x in feature_templates['data']:
    for y in template_collection:
        if y in x["templateName"]: 
            if not "V01" in y: 
                #update_dict = {x["templateName"]: x["templateId"]}
                data = {"templateName":x["templateName"],"templateId":x["templateId"]}
                template_collection_json.append(data)
                break

for x in feature_templates['data']:
    for y in template_collection_cEdge:
        if y in x["templateName"]: 
            #update_dict = {x["templateName"]: x["templateId"]}
            data = {"templateName":x["templateName"],"templateId":x["templateId"]}
            template_collection_cEdge_json.append(data)
            break

for x in template_collection_json:
    res = sdwanp.get_request("template/feature/definition/" + x["templateId"])
    res_json = json.loads(res)
    template = json.dumps(res_json, indent=2)
    f = open("./default_template/"+x['templateName']+".json", "w")
    f.write(template)
    f.close()

for x in template_collection_cEdge_json:
    res = sdwanp.get_request("template/feature/definition/" + x["templateId"])
    res_json = json.loads(res)
    template = json.dumps(res_json, indent=2)
    f = open("./default_template_cEdge/"+x['templateName']+".json", "w")
    f.write(template)
    f.close()

####################################################
# Define model supported list from Default template 
####################################################
#print(template_collection_cEdge_json)
#res = sdwanp.get_request("template/feature/object/" + template_collection_cEdge_json[1]["templateId"])
#res_json = json.loads(res)
#cedge_model_list = res_json['deviceType']

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

all_model_list = vedge_model_list+cedge_model_list

####################################################
# GET CONFIGURAITON FROM CONFIG.JSON
####################################################
with open("./config/config.json") as f: 
   config_data = json.load(f)

##########################
# Run UIInput.py
##########################
#template_payload = create_payload()
#print(template_payload)

##########################
# Configure Template 
##########################

###############################################
# Standard Template : BFD, OMP 
###############################################
if 'true' in config_data['global_omp'] :
    omp_result_vEdge = sdwanp.post_request("template/feature",create_omp_payload("Standard_vEdge",vedge_model_list),headers={'Content-Type': 'application/json'})
    omp_result_cEdge = sdwanp.post_request("template/feature",create_omp_cEdge_payload("Standard_cEdge",cedge_model_list),headers={'Content-Type': 'application/json'})

if 'true' in config_data['global_bfd'] :    
    bfd_result_vEdge = sdwanp.post_request("template/feature",create_bfd_payload("Standard_vEdge",vedge_model_list),headers={'Content-Type': 'application/json'})
    bfd_result_cEdge = sdwanp.post_request("template/feature",create_bfd_cEdge_payload("Standard_cEdge",cedge_model_list),headers={'Content-Type': 'application/json'})


###############################################
# VPN | Interface Template : 
###############################################
for x in config_data['edge_router']:
   
    site = x['prefix']
    model = x['model']

    ###############################################
    # VPN | Interface Template 
    ###############################################
    ###############################################
    ## vEdge Templete
    ###############################################
    if model in vedge_model_list :
        # WAN VPN 
        sdwanp.post_request("template/feature",create_vpn_payload(site,model,vpn="0",vpn_routes=x['wan_route']),headers={'Content-Type': 'application/json'})
        
        # LAN VPN 1 
        sdwanp.post_request("template/feature",create_vpn_payload(site,model,vpn="1",vpn_routes=0),headers={'Content-Type': 'application/json'})
        
        # WAN interface
        for interface in x['interface']['wan'] :
            parent_interface = 'n/a'
            if 'y' in interface['nat_type']:
                nat_type = 'true'
            else :  
                nat_type = 'false'
            if "." in interface["if_name"]: 
                sdwanp.post_request("template/feature",create_int_payload(site,model,interface["if_name"],interface["ip_type"],"true",nat_type,'false',interface['restrict']),headers={'Content-Type': 'application/json'})
                temp_if_name = interface["if_name"]
                parent_interface = temp_if_name.split(".",1)
                sdwanp.post_request("template/feature",create_int_payload(site,model,parent_interface[0],"null","false","false",'false','false'),headers={'Content-Type': 'application/json'})
            else :
                sdwanp.post_request("template/feature",create_int_payload(site,model,interface["if_name"],interface["ip_type"],"true",nat_type,'false',interface['restrict']),headers={'Content-Type': 'application/json'})   
            print("WAN " +interface['if_name'] + " template has been created.")

         
        # LAN interface
        for interface in x['interface']['lan'] :
            if "." in interface["if_name"]: 
                sdwanp.post_request("template/feature",create_int_payload(site,model,interface["if_name"],interface["ip_type"],"false",'false','false','false'),headers={'Content-Type': 'application/json'})
                temp_if_name = interface["if_name"]
                parent_interface = temp_if_name.split(".",1)
                sdwanp.post_request("template/feature",create_int_payload(site,model,parent_interface[0],"null","false","false",'false','false'),headers={'Content-Type': 'application/json'})
            else :
                sdwanp.post_request("template/feature",create_int_payload(site,model,interface["if_name"],interface["ip_type"],"false",'false','false','false'),headers={'Content-Type': 'application/json'})
            #print("LAN template has been created.")

        # Mgmt Interface 
        for interface in x['interface']['mgmt'] :
            if 'true' in interface['oob_mgmt'] :
                sdwanp.post_request("template/feature",create_int_payload(site,model,interface['if_name'],'static',"false",'false','true','false'),headers={'Content-Type': 'application/json'})
                print("MGMT template has been created.")
    
    ###############################################
    ## cEdge IOS-XE Templete
    ###############################################
    if model in cedge_model_list :
        # WAN VPN 
    
        sdwanp.post_request("template/feature",create_vpn_cEdge_payload(site,model,vpn="0",vpn_routes=x['wan_route']),headers={'Content-Type': 'application/json'})
        
        # LAN VPN 1 
        sdwanp.post_request("template/feature",create_vpn_cEdge_payload(site,model,vpn="1",vpn_routes=0),headers={'Content-Type': 'application/json'})
        
        # WAN interface
        for interface in x['interface']['wan'] :
            parent_interface = 'n/a'
            if 'y' in interface['nat_type']:
                nat_type = 'true'
            else :  
                nat_type = 'false'
            if "." in interface["if_name"]: 
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,interface["if_name"],interface["ip_type"],"true",nat_type,'false',interface['restrict']),headers={'Content-Type': 'application/json'})
                temp_if_name = interface["if_name"]
                parent_interface = temp_if_name.split(".",1)
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,parent_interface[0],"null","false","false",'false','false'),headers={'Content-Type': 'application/json'})
            else :
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,interface["if_name"],interface["ip_type"],"true",nat_type,'false',interface['restrict']),headers={'Content-Type': 'application/json'})   
            print("WAN " +interface['if_name'] + " template has been created.")

         
        # LAN interface
        for interface in x['interface']['lan'] :
            if "." in interface["if_name"]: 
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,interface["if_name"],interface["ip_type"],"false",'false','false','false'),headers={'Content-Type': 'application/json'})
                temp_if_name = interface["if_name"]
                parent_interface = temp_if_name.split(".",1)
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,parent_interface[0],"null","false","false",'false','false'),headers={'Content-Type': 'application/json'})
            else :
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,interface["if_name"],interface["ip_type"],"false",'false','false','false'),headers={'Content-Type': 'application/json'})
            print("LAN template has been created.")

        # Mgmt Interface 
        #input()
        #print(x['interface']['mgmt']['oob_mgmt'])
        for interface in x['interface']['mgmt'] :
            if 'true' in interface['oob_mgmt'] :
                sdwanp.post_request("template/feature",create_int_cEdge_payload(site,model,interface['if_name'],'static',"false",'false','true','false'),headers={'Content-Type': 'application/json'})
                print("MGMT template has been created.")


            
##########################
# Localized Policy Section
##########################

if 'true' in config_data['global_qos'] :
    # Configure Class_map list - Queue 0 - 3 
    class_map_payload = create_class_map_list_payload(3)
    for x in class_map_payload:
        class_map_id = sdwanp.post_request("template/policy/list/class",x,headers={'Content-Type': 'application/json'})
        #print (class_map_id)

    # Configure qos_map
    get_qos_ref = sdwanp.get_request("template/policy/list/class")
    get_qos_ref_json = json.loads(get_qos_ref)
    qos_map_payload = create_qos_map_payload(get_qos_ref_json["data"])
    qos_map_created = sdwanp.post_request("template/policy/definition/qosmap",qos_map_payload,headers={'Content-Type': 'application/json'})
    qos_map_created_json = json.loads(qos_map_created)
    print("qos_map has been created.")
    qos_map_id = qos_map_created_json["definitionId"]
    #print(qos_map_id)

    # Configure Standard Localized Policy 
    localized_policy_payload = create_localized_policy_payload(qos_map_id)
    localized_policy_created = sdwanp.post_request("template/policy/vedge",localized_policy_payload,headers={'Content-Type': 'application/json'})
    print("Initial Localized policy has been created.")












