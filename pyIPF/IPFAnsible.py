#!/usr/bin/env python3

'''
Script to test pyIPF module to fetch inventory and write it out as an Ansible inventory

Set environment variables:

IPF_SERVER = DNS/IP and port of IP Fabric server
IPF_USER = API username
IPF_PASSWORD = API user password
'''

from pyIPF import getIPFInventory, writeAnsibleInventory, writeAnsibleHostVars, pyIPFLog
import sys
import os

def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    IPFServer = os.getenv('IPF_SERVER')
    IPFUser = os.getenv('IPF_USER')
    IPFPassword = os.getenv('IPF_PASSWORD')

    if len(IPFServer)>0 and len(IPFUser)>0 and len(IPFPassword)>0:
        try:
            devs=getIPFInventory(IPFServer,IPFUser,IPFPassword)
            if '--list' in opts:
                if len(devs)>0:
                    writeAnsibleInventory(devs,'json')
            elif '--host' in opts:
                if len(devs)>0:
                    writeAnsibleHostVars(devs,args[0],'json')
        except:
            pyIPFLog("Parameter error calling getIPFInventory")

if __name__ == "__main__":
    main()