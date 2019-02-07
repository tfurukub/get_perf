##############################################################################
#
#  Script: Get Performance Data via REST API (v1)
#  Author: Takeo Furukubo
#  Description: Get the performance data of each VM
#  Language: Python2.7
#
##############################################################################

import pprint
import json
import requests
from datetime import datetime
import time


v1_BASE_URL = 'https://{}:9440/PrismGateway/services/rest/v1/'
POST = 'post'
GET = 'get'

class NtnxRestApi:
    def __init__(self, cluster_ip, username, password):
        self.cluster_ip = cluster_ip
        self.username = username
        self.password = password
        self.v1_url = v1_BASE_URL.format(self.cluster_ip)
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
            request_url = self.v1_url + sub_url
            server_response = self.session.get(request_url)
        elif method_type == POST:
            request_url = self.v1_url + sub_url
            server_response = self.session.post(request_url, payload_json)
        else:
            print("method type is wrong!")
            return

        #print("Response code: {}".format(server_response.status_code))
        return server_response.status_code, json.loads(server_response.text)

    def get_vmlist(self):
        #print("Getting list of VMs")
        rest_status, response = self.rest_call(GET, 'vms', None)

        with open('vms.json', 'wt') as fout:
            json.dump(response, fout, indent=2)
        return rest_status, response

    def get_vm_perf(self,vm_uuid,start,end,interval,metric):
        sub_url = "vms/"+vm_uuid+"/stats"+"/?metrics="+metric+"&startTimeInUsecs="+start+"&endTimeInUsecs="+end+"&intervalInSecs="+interval
        rest_status, response = self.rest_call(GET,sub_url,None)
        return rest_status, response

    def set_metric(self,metric_list):
        metric = ""
        for metric_item in metric_list:
          metric = metric+metric_item+"%2C"
        metric = metric[:-3]
        return metric

if __name__ == "__main__":
    try:
        pp = pprint.PrettyPrinter(indent=2)

        # Establish connection with a specific NTNX Cluster
        tgt_cluster_ip = "172.16.10.105"  # Please specify a target cluster external IP Address
        tgt_username = "admin"  # Please specify a user name of target cluster
        tgt_password = "Nutanix/4u!"  # Please specify the password of the user
        rest_api = NtnxRestApi(tgt_cluster_ip, tgt_username, tgt_password)
        # Get VM List
        status,vms = rest_api.get_vmlist()

        # Get Performance Data
        # Define the start and end time (in microseconds as unixtime). Start time is now
        hours = 6
        interval = 30 #in second
        now = datetime.now()
        #end = int(time.mktime(now.timetuple())) * 1000000
        #start = int(end - hours * 3600 * 1000000)
        start = int(1548896400 * 1000000)
        end = (start + hours * 3600 * 1000000)

        # Define the metric
        #metric_list = ["hypervisor_write_io_bandwidth_kBps","hypervisor_read_io_bandwidth_kBps","hypervisor_avg_write_io_latency_usecs","hypervisor_avg_read_io_latency_usecs"]
        #metric_list = ["hypervisor_total_write_io_size_kbytes","hypervisor_total_read_io_size_kbytes"]
        metric_list = ["hypervisor_total_write_io_size_size"]
        metric = rest_api.set_metric(metric_list)
        #print(metric)

        for entity_vm in vms.get("entities"):
            if(entity_vm.get('uuid') == "ef56c77b-355a-4df2-abd0-4c93c1aca7ae"):
              #print("{0}  {1}".format(entity_vm.get('vmName'),entity_vm.get('uuid')))
              status,perf = rest_api.get_vm_perf(entity_vm.get('uuid'),str(start),str(end),str(interval),metric)
              print(perf)

              perf_data = {}
              for entity_perf in perf.get("statsSpecificResponses"):
                  num_values = range(len(entity_perf.get('values')))
                  metric_item = entity_perf.get("metric")
                  perf_item_data = []
                  for i in num_values:
                      perf_item_data.append(entity_perf.get('values')[i])
                      t =  start/1000000 + i*interval
                      #print("{0}  {1}".format(datetime(*time.localtime(t)[:6]),entity_perf.get('values')[i]))
                  perf_data[metric_item] = perf_item_data

              item = ""

              for m in metric_list:
                print(m+","),
              print("")
              for i in num_values:
                display_string = ""
                t =  start/1000000 + i*interval
                display_string = display_string +str( datetime(*time.localtime(t)[:6]))
                for k in perf_data:
                  display_string = display_string + "," + str(perf_data[k][i])
                print(display_string)

    except Exception as ex:
        print(ex)
        exit(1)
