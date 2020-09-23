#!/usr/bin/env python3

'''
Script to use pyIPF module to fetch IPF route data and diff it with previous snapshot

'''

from pyIPF import getIPFInventory, writeInventoryTable, fetchIPFAccessToken, getIPFData
import sys
import json
import os
from dotenv import load_dotenv

def fetchIPFRoutes(IPFServer,hostName,snapshot,APIToken='',IPFUser='',IPFPassword=''):
    '''
    Function to fetch the list of route entries for the device hostName from snapshot

    IPFServer = name or IP address of IP Fabric Server
    hostName = name of device to fetch rout entries
    snapshot = id or one of ['$last','$prev','$lastlocked']
    APIToken = v3.7+ API Token
    IPFUser = -v3.7 IPF username
    IPFPassword = -v3.7 IPF password

    Returns dictionary of routing entries

    '''

    if APIToken != '':
        #assume v3.7 or above
        headers = {'X-API-Token' : APIToken, 'Content-type':'application/json'}
        routesPayload={
            "columns":["id","sn","hostname","siteKey","siteName","network","prefix","protocol","vrf","nhCount","nhLowestAge","nhLowestMetric","nexthop"],
            "filters":{"hostname":["eq",hostName]},
            "snapshot":snapshot,
            "reports":"/technology/routing/routes"
        }
        routesEndpoint='http://'+IPFServer+'/v1/tables/networks/routes'
        routes=getIPFData(routesEndpoint,headers,routesPayload)
    else:
        #assume version lower than 3.7
        routes={}

    return (routes)


def main():

    load_dotenv()
    IPFServer = os.getenv('IPF_SERVER')
    IPFFilter = os.getenv('IPF_FILTER')
    IPFToken = os.getenv('IPF_TOKEN')

    lastroutes=fetchIPFRoutes(IPFServer,'L1R1','$last',APIToken=IPFToken)
    print(json.dumps(lastroutes.json(),indent=4))

    prevroutes=fetchIPFRoutes(IPFServer,'L1R1','$prev',APIToken=IPFToken)
    print(json.dumps(prevroutes.json(),indent=4))

if __name__ == "__main__":
    main()