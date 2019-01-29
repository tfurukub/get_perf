##############################################################################
#
#  Script: Create VMs on Nutanix Cluster via REST API (v2)
#  Author: Yukiya Shimizu
#  Description: Create VMs on Nutanix Cluster with Cloud-Init
#  Language: Python3
#
##############################################################################

import pprint
import json
import yaml
import requests
from datetime import datetime
import time


# v1_BASE_URL = 'https://{}:9440/PrismGateway/services/rest/v1/'
# self.v1_url = v1_BASE_URL.format(self.cluster_ip)
v2_BASE_URL = 'https://{}:9440/PrismGateway/services/rest/v1/'
POST = 'post'
GET = 'get'

class NtnxRestApi:
    def __init__(self, cluster_ip, username, password):
        self.cluster_ip = cluster_ip
        self.username = username
        self.password = password
        self.v2_url = v2_BASE_URL.format(self.cluster_ip)
        self.session = self.get_server_session()

    def get_server_session(self):
        # Creating REST client session for server connection, after globally setting.
        # Authorization, content type, and character set for the session.

        session = requests.Session()
        session.auth = (self.username, self.password)
        session.verify = False
        session.headers.update(
            {'Content-Type': 'application/json; charset=utf-8'})
        return session

    def rest_call(self, method_type, sub_url, payload_json):
        if method_type == GET:
            request_url = self.v2_url + sub_url
            server_response = self.session.get(request_url)
        elif method_type == POST:
            request_url = self.v2_url + sub_url
            server_response = self.session.post(request_url, payload_json)
        else:
            print("method type is wrong!")
            return

        print("Response code: {}".format(server_response.status_code))
        return server_response.status_code, json.loads(server_response.text)

    def get_cluster_info(self):
        print("Getting cluster information for cluster {}".format(self.cluster_ip))
        rest_status, response = self.rest_call(GET, 'clusters', None)

        with open('cluster.json', 'wt') as fout:
            json.dump(response, fout, indent=2)
        return rest_status, response

    def get_cluster_info(self):
        print("Getting cluster information for cluster {}".format(self.cluster_ip))
        rest_status, response = self.rest_call(GET, 'clusters', None)

        with open('cluster.json', 'wt') as fout:
            json.dump(response, fout, indent=2)
        return rest_status, response

    def get_vmlist(self):
        print("Getting list of VMs")
        rest_status, response = self.rest_call(GET, 'vms', None)

        with open('vms.json', 'wt') as fout:
            json.dump(response, fout, indent=2)
        return rest_status, response

    def get_networks_info(self):
        print("Getting networks information for cluster {}".format(self.cluster_ip))
        rest_status, response = self.rest_call(GET, 'networks', None)

        with open('networks.json', 'wt') as fout:
            json.dump(response, fout, indent=2)
        return rest_status, response

    def get_vm_perf(self,vm_uuid,start,end,interval):
        sub_url = "vms/"+vm_uuid+"/stats"+"/?metrics=hypervisor_cpu_usage_ppm%2Cmemory_usage_ppm&startTimeInUsecs="+start+"&endTimeInUsecs="+end+"&intervalInSecs="+interval
        rest_status, response = self.rest_call(GET,sub_url,None)
        return rest_status, response


if __name__ == "__main__":
    try:
        pp = pprint.PrettyPrinter(indent=2)

        # Establish connection with a specific NTNX Cluster
        tgt_cluster_ip = "172.16.10.119"  # Please specify a target cluster external IP Address
        tgt_username = "admin"  # Please specify a user name of target cluster
        tgt_password = "Nutanix/4u!"  # Please specify the password of the user
        rest_api = NtnxRestApi(tgt_cluster_ip, tgt_username, tgt_password)
        # Get VM List
        status,vms = rest_api.get_vmlist()

        # Get Performance Data
        days = 1
        now = datetime.now()
        end = int(time.mktime(now.timetuple())) * 1000000
        start = end - days * 24 * 36 * 1000000
        cpu_usage = {}
        mem_usage = {}
        for entity in vms.get("entities"):
            print("Name: {}".format(entity.get('vmName')))
            print("uuid: {}".format(entity.get('uuid')))
            status,perf = rest_api.get_vm_perf(entity.get('uuid'),str(start),str(end),"30")
            for entity2 in perf.get("statsSpecificResponses"):
                num_values = range(len(entity2.get('values')))
                for i in num_values:
                    t =  start/1000000 + i*30
                    if entity2.get('metric') == "hypervisor_cpu_usage_ppm":
                        cpu_usage[datetime(*time.localtime(t)[:6])] = entity2.get('values')[i]
                    if entity2.get('metric') == "memory_usage_ppm":
                        mem_usage[datetime(*time.localtime(t)[:6])] = entity2.get('values')[i]
                    
            for key,value in sorted(cpu_usage.items()):
              print key,cpu_usage[key],mem_usage[key]
            cpu_usage.clear()
            mem_usage.clear()

        print("=" * 79)

    except Exception as ex:
        print(ex)
        exit(1)
