#!/usr/bin/env python3

'''
Module to expose IP Fabric APIs as functions to other Python scripts:

def pyIPFLog (msg):  Function to write a log message using logging module
def fetchIPFAccessToken (IPFServer, userAndPass):  Function to authenticate a user and fetch the token for API calls
def refreshIPFToken (IPFServer, refreshToken):  Function to refresh the access token for API calls
def getIPFData(apiEndpoint, dataHeaders, dataPayload):  Function to fetch arbitrary data from IP Fabric server
def getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):  Function to retrieve IP Fabric inventory details
'''

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
    '''
    Function to write a log message using logging module

    msg = text for the message to be logged

    Returns:  True if message logged  
    '''
    if (msg!=''):
        logging.basicConfig(filename='./pyIPF.log',level=logging.INFO)
        logging.info(str(datetime.now())+' '+msg)
        retVal=True
    else:
        retVal=False
    return retVal

def fetchIPFAccessToken (IPFServer, userAndPass):
    '''
    Function to authenticate a user and fetch the token for API calls

    IPFServer = IP address or DNS name of IP Fabric server
    userAndPass = dictionary containing GUI login credentials in the form:
        {
            'username':<username>,
            'password':<password>
        }

    Returns:    dictionary containing access token (which lasts 30 minutes) and refresh token (24 hour life span) in the form:
        {
            'accessToken':<token>,
            'refreshToken':<token>
        }
    '''
    authPost = requests.post('https://' + IPFServer + '/api/v1/auth/login', json=userAndPass, verify=False)
    if authPost.ok: 
        pyIPFLog('User authenticated successfully')
    else: 
        pyIPFLog('User NOT authenticated: ' + str(authPost.reason) + ',  \n  Error: ' + authPost.text)
    return authPost

def refreshIPFToken (IPFServer, refreshToken):
    '''
    Function to refresh the access token for API calls

    IPFServer = IP address or DNS name of IP Fabric server
    refreshToken = refresh token from fetchIPFAccessToken response

    Returns:    dictionary containing new access token in the form:
        {
            'accessToken':<token>
        }
    '''
    refreshPost = requests.post('https://' + IPFServer + '/api/v1/auth/token', json={'refreshToken': refreshToken}, verify=False)
    if refreshPost.ok:
        pyIPFLog('Token refreshed successfully')
    else:
        pyIPFLog('Unable to refresh the token: ' + refreshPost.text)
    return refreshPost

def getIPFData(apiEndpoint, dataHeaders, dataPayload):
    '''
    Function to fetch arbitrary data from IP Fabric server

    apiEndpoint = Full URL of API endnpoint
    dataHeaders = http headers for request (including authorisation token)
    dataPayload = dictionary with JSON representation of request parameters

    Returns:    dictionary containing JSON representation of response
    '''
    dataPost = requests.post(apiEndpoint, headers=dataHeaders, json=dataPayload, verify=False)
    if dataPost.ok:
        pyIPFLog('Successfully gathered data from: ' + apiEndpoint)
    else:
        pyIPFLog('Unable to get data from: ' + apiEndpoint + '\n  Error: ' + dataPost.text)
    return dataPost

def getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):
    '''
    Function to retrieve IP Fabric inventory details

    IPFServer = IP address or DNS name of IP Fabric server to query
    username / password = GUI credentials for IP Fabric server
    snapshotId = full ID of the snapshot for the inventory request *or* '$last', '$prev'
    columns = list of columns required from the inventory table
    filters = field filters as defined in the Table Description window

    Returns:    dictionary containing device information from IP Fabric to meet the criteria defined above. 
    '''
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
    '''
    Function to output inventory from getIPFInventory function and output it in a format suitable for use as an Ansible inventory

    filename = file to output or '' for stdout
    format = "yaml" or "json"
    grouping = list of group categories for inventory output - valid values are "site", "vendor", "access"
    devs = dictionary of devices from getIPFInventory

    Returns:    True if written OK to file or stdout / False if write failed
    '''
    inventory={}
    writeToFile=False
    RetVal=False

    # if filename passed, open the file to write to it
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

    # Prepare output in correct format
    if (format.upper()=='YAML'):
        output=yaml.dump({'all':{'children':inventory}})
    elif (format.upper()=='JSON'):
        output=json.dumps({'all':{'children':inventory}},indent=4)
    else:
        output=''

    if writeToFile:
        # write output to file
        try:
            print(output,file=f)
            f.close()
            retVal=True
            pyIPFLog(format.upper()+" format inventory successfully written to "+filename)
        except:
            pyIPFLog("Error writing "+format.upper()+ " format inventory to "+filename)
    else:
        # write output to stdout
        try:
            print(output)
            retVal=True
            pyIPFLog(format.upper()+" format inventory successfully written to stdout")
        except:
            pyIPFLog("Error writing "+format.upper()+ " format inventory to stdout")

def main():
    # Run test extraction
    try:
        devs=getIPFInventory('192.168.1.174','admin','netHero!123','$last',['hostname','siteName','loginIp','loginType','vendor'],'')
        if len(devs)>0:
            writeAnsibleInventory('','json',['access',"site"],devs)
    except:
        pyIPFLog("Parameter error calling getIPFInventory")


if __name__ == "__main__":
    main()