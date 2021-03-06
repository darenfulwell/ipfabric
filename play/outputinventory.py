#!/usr/bin/env python3

"""
Simple Python3 script for retrieving devices from the last snapshot and exporting as an Ansible inventory
"""

# Built-in/Generic Imports
from ipfapidemo import tokenRequest, getData
import json
import yaml
from time import sleep

# Global variables
server = 'https://demo4.ipf.ipfabric.io/'
# server = 'https://10.0.8.15/' 
authData = { 'username': 'ipfabricdemo', 'password' : 'ipfabricdemo' }
ipfabricInventory = 'hosts.json'
ansibleInventory = 'hosts.yaml'

# API call variables
snapshotId = '$last'
devicesEndpoint = server + 'api/v1/tables/inventory/devices'
devicesPayload = {
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

# Open inventory files
f=open(ansibleInventory,'w')
g=open(ipfabricInventory,'w')

# Extract device info from JSON returned from API
devs=json.loads(devices.content)["data"]
print(json.dumps(devs,indent=4), file=g)
g.close()

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
        inventory[v]={'hosts':{}}

    # Add devices to vendor group
    inventory[v]['hosts'][h]={}
    inventory[v]['hosts'][h]['ansible_host']=i
    inventory[v]['hosts'][h]['ansible_connection']=c

    # Create site grouping
    if not (s in inventory):
        inventory[s]={'hosts':{}}

    # Add devices to site group
    inventory[s]['hosts'][h]={}
    inventory[s]['hosts'][h]['ansible_host']=i
    inventory[s]['hosts'][h]['ansible_connection']=c

# write inventory in YAML to text file and close
print (yaml.dump({'all':{'children':inventory}}),file=f)
f.close()