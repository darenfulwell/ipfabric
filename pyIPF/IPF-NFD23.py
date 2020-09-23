#!/usr/bin/env python3

'''
Script to use pyIPF module to fetch IPF data and write it out as rich tables

'''

from pyIPF import getIPFInventory, writeInventoryTable, fetchIPFAccessToken, getIPFData
import sys
import json
import os

def main():
IPFServer='demo4.ipf.ipfabric.io'
username='ipfabricdemo'
password='ipfabricdemo'

devs=getIPFInventory(IPFServer,username,password,filters={'siteName':['like','L38']})
writeInventoryTable(devs)

authData = {'username':username, 'password':password}
interfacesEndpoint = 'https://'+ IPFServer + '/api/v1/tables/inventory/interfaces'
interfacesPayload = {
    "columns":["id","sn","hostname","intName","siteKey","siteName","l1","l2","reason","dscr","mac","duplex","speed","media","errDisabled","mtu","primaryIp"],
    "filters":{"siteName":["like","38"],"hostname":["like","R"],"l1":["like","down"],"l2":["like","down"]},
    "pagination":{"limit":23,"start":0},
    "snapshot":"b8dd2f79-3d5f-4bcd-835e-4dfdc454e0af",
    "reports":"/inventory/interfaces"
}

tokens = fetchIPFAccessToken(IPFServer, authData).json()
headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}
interfaces = getIPFData(interfacesEndpoint, headers, interfacesPayload)
print(json.dumps(interfaces.json(),indent=4))

if __name__ == "__main__":
    main()