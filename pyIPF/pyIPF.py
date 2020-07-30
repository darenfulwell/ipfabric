#!/usr/bin/env python3

"""
Simple module to handle IP Fabric inventories
"""

# Built-in/Generic Imports
import json
import yaml
from time import sleep
from datetime import datetime
import requests
import logging

# Suppressing SSL certificate warnings if needed
requests.packages.urllib3.disable_warnings()

# Defining main functions
def pyIPFLog (msg):
    if (msg!=''):
        logging.basicConfig(filename='./pyIPF.log',level=logging.INFO)
        logging.info(str(datetime.now())+' '+msg)
        retVal=True
    else:
        retVal=False
    return retVal

def fetchIPFAccessToken (IPFServer, userAndPass):
    authPost = requests.post('https://' + IPFServer + '/api/v1/auth/login', json=userAndPass, verify=False)
    if authPost.ok: 
        pyIPFLog('User authenticated successfully')
    else: 
        pyIPFLog('User NOT authenticated: ' + str(authPost.reason) + ',  \n  Error: ' + authPost.text)
    return authPost

def refreshIPFToken (IPFServer, refreshToken):
    refreshPost = requests.post('https://' + IPFServer + '/api/v1/auth/token', json={'refreshToken': refreshToken}, verify=False)
    if refreshPost.ok:
        pyIPFLog('Token refreshed successfully')
    else:
        pyIPFLog('Unable to refresh the token: ' + refreshPost.text)
    return refreshPost

def getIPFData(apiEndpoint, dataHeaders, dataPayload):
    dataPost = requests.post(apiEndpoint, headers=dataHeaders, json=dataPayload, verify=False)
    if dataPost.ok:
        pyIPFLog('Successfully gathered data from: ' + apiEndpoint)
    else:
        pyIPFLog('Unable to get data from: ' + apiEndpoint + '\n  Error: ' + dataPost.text)
    return dataPost

def getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):
    retVal={}
    if (len(IPFServer)>0):
        if (username!='') and (password!=''):
            # assemble authentication data for token request
            authData = {'username':username, 'password':password}

            # set defaults if parameters are null
            if (snapshotId==''):
                snapshotId='$last'
            if (len(columns)==0):
                columns=["hostname","siteName","loginIp","loginType","vendor","platform","family"]
            if (len(filters)==0):
                filters={}

            #assemble inventory request to IPF
            devicesEndpoint = 'https://'+ IPFServer + '/api/v1/tables/inventory/devices'
            devicesPayload = {
                'columns':columns,
                'filters':filters,
                'pagination':{"limit":500,"start":0},
                'snapshot':snapshotId,
                'reports':"/inventory/devices"
            }

            # Authenticate and assemble request headers
            tokens = fetchIPFAccessToken(IPFServer, authData).json()
            headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}

            # API call to pull device list
            try:
                devices = getIPFData(devicesEndpoint, headers, devicesPayload)

                 # Extract device info from JSON returned from API
                retVal=json.loads(devices.content)["data"]
            except:
                pyIPFLog('API request failed')

        else:
            pyIPFLog('Invalid username and/or password parameter')
    else:
        pyIPFLog('Invalid IPF Server parameter')

    return retVal

def writeAnsibleInventory (filename, format, grouping, devs):
    inventory={}
    writeToFile=False
    RetVal=False

    if len(filename)>0:
        f=open(filename,'w')
        writeToFile=True

    # Loop through passed devices
    for dev in devs:

        # Extract data for inventory
        h=dev['hostname']['data']
        i=dev['loginIp']
        v=dev['vendor']
        c=dev['loginType']
        s=dev['siteName']
    
        if ("vendor" in grouping):
            # Create vendor grouping
            if not (v in inventory):
                inventory[v]={'hosts':{}}

            # Add devices to vendor group
            inventory[v]['hosts'][h]={}
            inventory[v]['hosts'][h]['ansible_host']=i
            inventory[v]['hosts'][h]['ansible_connection']=c

        if ("site" in grouping):
            # Create site grouping
            if not (s in inventory):
                inventory[s]={'hosts':{}}

            # Add devices to site group
            inventory[s]['hosts'][h]={}
            inventory[s]['hosts'][h]['ansible_host']=i
            inventory[s]['hosts'][h]['ansible_connection']=c

        if ("access" in grouping):
            # Create access method grouping
            if not (c in inventory):
                inventory[c]={'hosts':{}}

            # Add devices to access group
            inventory[c]['hosts'][h]={}
            inventory[c]['hosts'][h]['ansible_host']=i
            inventory[c]['hosts'][h]['ansible_connection']=c

    if (format.upper()=='YAML'):
        # write inventory in YAML to text file and close
        output=yaml.dump({'all':{'children':inventory}})
    elif (format.upper()=='JSON'):
        output=json.dumps({'all':{'children':inventory}},indent=4)
    else:
        output=''

    if writeToFile:
        try:
            print(output,file=f)
            f.close()
            retVal=True
            pyIPFLog(format.upper()+" format inventory successfully written to "+filename)
        except:
            pyIPFLog("Error writing "+format.upper()+ " format inventory to "+filename)
    else:
        try:
            print(output)
            retVal=True
            pyIPFLog(format.upper()+" format inventory successfully written to stdout")
        except:
            pyIPFLog("Error writing "+format.upper()+ " format inventory to stdout")

def main():
    # Extract device info from JSON returned from API
    devs=getIPFInventory('192.168.1.174','admin','netHero!123','$last',['hostname','siteName','loginIp','loginType','vendor'],{'vendor':["like","arista"]})
    writeAnsibleInventory('','json',['access',"site"],devs)


if __name__ == "__main__":
    main()