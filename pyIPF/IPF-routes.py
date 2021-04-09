#!/usr/bin/env python3

'''
Script to use pyIPF module to fetch IPF route data and diff it with previous snapshot

'''

from pyIPF import getIPFInventory, writeInventoryTable, fetchIPFAccessToken, getIPFData
import sys
import json
import os
from dotenv import load_dotenv
from rich.table import Table
from rich.console import Console
from operator import itemgetter

def print_table(data):
    lengths = [
        [len(str(x)) for x in row]
        for row in data
    ]

    max_lengths = [
        max(map(itemgetter(x), lengths))
        for x in range(0, len(data[0]))
    ]

    format_str = ''.join(map(lambda x: '%%-%ss | ' % x, max_lengths))

    print(format_str % data[0])
    print('-' * (sum(max_lengths) + len(max_lengths) * 3 - 1))

    for x in data[1:]:
        print(format_str % x)


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
        routesEndpoint='https://'+IPFServer+'/api/v1/tables/networks/routes'
        routes=getIPFData(routesEndpoint,headers,routesPayload)
    else:
        #assume version lower than 3.7
        routes={}

    return (routes)

def routeEntries(IPFRoutes):
    '''
    Function to convert IPF route data to list of tuples

    IPFRoutes = Dictionary output from fetchIPFRoutes()

    Returns a list of tuples
    '''

    routeEntryList=[('hostname','network','protocol','vrf','next hop','int','AD')]
    
    for routeEntry in IPFRoutes.json()['data']: 
        for nextHop in routeEntry['nexthop']:
            newEntry=(routeEntry['hostname'],routeEntry['network'],routeEntry['protocol'],routeEntry['vrf'],nextHop['ip'],nextHop['intName'],nextHop['ad'])
            routeEntryList.append(newEntry)

    return routeEntryList

def diffRoutes (oldRoutes,newRoutes):
    '''
    Function to work out what has changed in route tables between snapshots

    oldRoutes = list of tuples containing routes from older snapshot returned from routeEntries() function
    newRoutes = list of tuples containing routes from older snapshot returned from routeEntries() function

    Returns addedRoutes, deletedRoutes
    '''

    newSorted=sorted(newRoutes, key=lambda tup:(tup[1], tup[2], tup[4], tup[5]))
    oldSorted=sorted(oldRoutes, key=lambda tup:(tup[1], tup[2], tup[4], tup[5]))
    addedRoutes = list(set(newSorted).difference(oldSorted))
    addedRoutes.insert(0,('hostname','network','protocol','vrf','next hop','int','AD'))
    deletedRoutes = list(set(oldSorted).difference(newSorted))
    deletedRoutes.insert(0,('hostname','network','protocol','vrf','next hop','int','AD'))
    return addedRoutes, deletedRoutes


def main():

    load_dotenv()
    IPFServer = os.getenv('IPF_SERVER')
    IPFFilter = os.getenv('IPF_FILTER')
    IPFToken = os.getenv('IPF_TOKEN')

    lastRoutes=routeEntries(fetchIPFRoutes(IPFServer,'L45EXR1','$last',APIToken=IPFToken))
    prevRoutes=routeEntries(fetchIPFRoutes(IPFServer,'L45EXR1','$prev',APIToken=IPFToken))

    diff=diffRoutes(prevRoutes,lastRoutes)

    print("Added routes:")
    print_table(diff[0])
    print("\nDeleted routes:")
    print_table(diff[1])

if __name__ == "__main__":
    main()
