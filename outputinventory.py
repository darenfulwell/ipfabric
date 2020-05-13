#!/usr/bin/env python3

"""
Simple Python3 script for retrieving devices from the last snapshot and exporting as an Ansible inventory
"""

# Built-in/Generic Imports
from ipfapi import tokenRequest, getData
import json
import yaml
from time import sleep

# Global variables
server = 'https://demo4.ipf.ipfabric.io/'
authData = { 'username': 'ipfabricdemo', 'password' : 'ipfabricdemo' }
ansibleInventory = 'hosts.yaml'

# API call variables
snapshotId = '$last'
devicesEndpoint = server + 'api/v1/tables/inventory/devices'
devicesPayload = {
#  'columns':["id","sn","hostname","siteKey","siteName","rd","stpDomain","loginIp","loginType","uptime","reload","memoryUtilization","vendor","platform","family","configReg","version","processor"],
  'columns':["hostname","siteName","loginIp","loginType","vendor","platform","family"],
  'filters':{},
  'pagination':{"limit":500,"start":0},
  'snapshot':snapshotId,
  'reports':"/inventory/devices"
}

# Assemble headers
tokens = tokenRequest(server, authData).json()
headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}

# API call to pull device list
devices = getData(devicesEndpoint, headers, devicesPayload)

# Open Ansible inventory
f=open(ansibleInventory,'w')

# Extract device info from JSON returned from API
devs=json.loads(devices.content)["data"]

inventory={}

# Loop through returned devices
for dev in devs:

    # Extract data for inventory
    h=dev['hostname']['data']
    i=dev['loginIp']
    v=dev['vendor']
    c=dev['loginType']
    s=dev['siteName']
    
    # Create vendor grouping
    if not (v in inventory):
        inventory[v]={}

    # Add devices to vendor group
    inventory[v][h]={}
    inventory[v][h]['ansible_host']=i
    inventory[v][h]['ansible_connection']=c

    # Create site grouping
    if not (s in inventory):
        inventory[s]={}

    # Add devices to site group
    inventory[s][h]={}
    inventory[s][h]['ansible_host']=i
    inventory[s][h]['ansible_connection']=c

# write inventory in YAML to text file and close
print (yaml.dump({'all':{'children':inventory}}),file=f)
f.close()