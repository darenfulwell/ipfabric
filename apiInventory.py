"""
Simple Python3 script for authenticating to IP Fabric's API and collecting inventory data
"""
# Built-in/Generic Imports
from ipfapi import tokenRequest, getData

# Starting with variables
server = 'https://demo4.ipf.ipfabric.io/'
authData = { 'username': 'ipfabricdemo', 'password' : 'ipfabricdemo' }

# Starting with endpont and payload variables
snapshotId = '2d7cb154-5d37-4acd-873d-7958dec60817'
devicesEndpoint = server + 'api/v1/tables/inventory/devices'
#devicesPayload = {'columns':["sn","hostname", "vendor"],'snapshot':snapshotId}
devicesPayload = {
  'columns':["id","sn","hostname","siteKey","siteName","rd","stpDomain","loginIp","loginType","uptime","reload","memoryUtilization","vendor","platform","family","configReg","version","processor"],
  'filters':{},
  'pagination':{"limit":500,"start":0},
  'snapshot':snapshotId,
  'reports':"/inventory/devices"
}

managedIpEndpoint = server + 'api/v1/tables/addressing/managed-devs'
manIpPayload = {'columns':["ip"], 'filters':{"intName":["like","lo"]}, 'snapshot':snapshotId}

# Working with tokens and creating headers
tokens = tokenRequest(server, authData).json()
headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}

# Main functions for testing in the console
devices = getData(devicesEndpoint, headers, devicesPayload)
mIps = getData(managedIpEndpoint, headers, manIpPayload)
print("Hello world")