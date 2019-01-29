# -*- coding: utf-8 -*-
import os
import re
import subprocess
import getpass
cluster_ip = "172.16.10.123"
user = "nutanix"
computer_name_list = []
with open('list3.csv','r') as f1:
    for line1 in f1:
        s = line1.strip().split(',')
        xmlfile = s[0] + ".xml"
        computer_name_list.append(s[0])
        with open(xmlfile,'w') as f3:
            with open('test.xml','r') as f2:
                for line2 in f2:
                    src = line2.strip()  
                    if re.findall('PC001',src):
                        dst = re.sub('PC001',s[0],src)
                        f3.write(dst+'\n')
                    elif re.findall('ipv4 set address',src):
                        dst = '<Path>NETSH interface ipv4 set address "イーサネット" static ' +  s[1] + ' 255.255.0.0 172.16.10.1</Path>'
                        f3.write(dst+'\n')
                    elif re.findall('ipv4 set dns',src):
                        dst = '<Path>NETSH interface ipv4 set dns "イーサネット" static 172.16.10.1 primary</Path>'
                        f3.write(dst+'\n')
                    else:
                        f3.write(src+'\n')
        cp_cmd = 'cp '+xmlfile+' /var/www/html'
        acli_cmd = 'sshpass -p nutanix/4u ssh '+user+'@'+cluster_ip+' /usr/local/nutanix/bin/acli uhura.vm.clone_with_customize '+s[0]+' clone_from_vm=win10_master sysprep_config_path=http://172.16.10.150/'+xmlfile+' container=5a835c58-38f3-4767-bf5e-40896cfa42bf'
        
        all_name = ""
        for computer_name in computer_name_list:
            all_name = all_name + computer_name + ","
        vm_on_cmd = 'sshpass -p nutanix/4u ssh '+user+'@'+cluster_ip+' /usr/local/nutanix/bin/acli vm.on '+all_name.strip(',')


        os.system(cp_cmd)
        os.system(acli_cmd)
os.system(vm_on_cmd)
            

