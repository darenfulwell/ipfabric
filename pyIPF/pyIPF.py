#!/usr/bin/env python3

'''
Module to expose IP Fabric APIs as functions to other Python scripts:

def pyIPFLog (msg):  Function to write a log message using logging module
def fetchIPFAccessToken (IPFServer, userAndPass):  Function to authenticate a user and fetch the token for API calls
def refreshIPFToken (IPFServer, refreshToken):  Function to refresh the access token for API calls
def getIPFData(apiEndpoint, dataHeaders, dataPayload):  Function to fetch arbitrary data from IP Fabric server
def getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):  Function to retrieve IP Fabric inventory details
def writeAnsibleInventory (devices, format, destination, grouping, variables): Function to write Ansible format inventory
def writeAnsibleHostVars (devices, hostName, format, filename, variables): Function to write Ansible format host variables
'''

# Built-in/Generic Imports
import json
import yaml
from time import sleep
from datetime import datetime
import requests
import logging
import sys

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

def getIPFInventory(IPFServer, username, password, snapshotId='$last', columns=["hostname","siteName","loginIp","loginType","vendor","platform","family","version","sn","devType"], filters={}):
    '''
    Function to retrieve IP Fabric inventory details

    IPFServer = IP address or DNS name of IP Fabric server to query
    username / password = GUI credentials for IP Fabric server
    snapshotId [optional] = full ID of the snapshot for the inventory request *or* '$last', '$prev' (default='$last')
    columns [optional] = list of columns required from the inventory table (default=["hostname","siteName","loginIp","loginType","vendor","platform","family","version","sn","devType"])
    filters [optional] = dictionary containing field filters as defined in the Table Description window in the Web UI (default={})

    Returns:    dictionary containing device information from IP Fabric to meet the criteria defined above. 
    '''
    retVal={}
    if (len(IPFServer)>0):
        if (username!='') and (password!=''):
            # assemble authentication data for token request
            authData = {'username':username, 'password':password}

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

def writeAnsibleInventory (devs, format, filename='', grouping=[], variables=[]):
    '''
    Function to output inventory from getIPFInventory function in a format suitable for use as an Ansible inventory
    
    devs = dictionary of devices from getIPFInventory
    format = "yaml" or "json"
    filename [optional] = file to output or '' for stdout (default is '')
    grouping [optional] = list of group categories for inventory output - valid values are "site", "access", "vendor", "platform", "model", "devType" (default is ungrouped)
    variables [optional] = additional hostvars (default is just ansible_host and ansible_connection)
    
    Returns:    True if written OK to file or stdout / False if write failed
    '''
    #wholeInventory={"all":{"children":{"ungrouped":{"hosts":[]}}},"_meta":{"hostvars":{}}}
    wholeInventory={"all":{"children":{"ungrouped":[]}},"_meta":{"hostvars":{}}}
    writeToFile=False
    RetVal=False

    # default set of additional hostvars = empty
    if len(variables)<1:
        variables=[]

    # Loop through passed devices
    for dev in devs:

        # Extract data for inventory
        h=dev['hostname']['data']
        i=dev['loginIp']
        v=dev['vendor']
        p=dev['platform']
        f=dev['family']
        o=dev['version']
        n=dev['sn']
        c=dev['loginType']
        s=dev['siteName']
        y=dev['devType']
    
        # inventory=wholeInventory['all']['children']

        # Add device hostvars
        wholeInventory['_meta']['hostvars'][h]={}
        wholeInventory['_meta']['hostvars'][h]['ansible_host']=i
        wholeInventory['_meta']['hostvars'][h]['ansible_connection']=c
        for var in variables:
            wholeInventory['_meta']['hostvars'][h][var]=dev[var]
 
        if len(grouping)==0:
            # if no groups specified, put host in 'ungrouped'
            # wholeInventory['all']['children']['ungrouped']['hosts'].append(h)
            wholeInventory['all']['children']['ungrouped'].append(h)
        else:
            if ("vendor" in grouping):
                # Create vendor grouping if needed
                if not (v in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][v]={'hosts':[]}
                    wholeInventory['all']['children'][v]=[]
                
                # Add device to vendor group
                #wholeInventory['all']['children'][v]['hosts'].append(h)
                wholeInventory['all']['children'][v].append(h)

            if ("site" in grouping):
                # Create site grouping
                if not (s in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][s]={'hosts':[]}
                    wholeInventory['all']['children'][s]=[]
                # Add device to site group
                #wholeInventory['all']['children'][s]['hosts'].append(h)
                wholeInventory['all']['children'][s].append(h)

            if ("access" in grouping):
                # Create access method grouping
                if not (c in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][c]={'hosts':[]}
                    wholeInventory['all']['children'][c]=[]
                # Add device to access group
                #wholeInventory['all']['children'][c]['hosts'].append(h)
                wholeInventory['all']['children'][c].append(h)

            if ("platform" in grouping):
                # Create platform grouping
                if not (p in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][p]={'hosts':[]}
                    wholeInventory['all']['children'][p]=[]
                # Add device to platform group
                #wholeInventory['all']['children'][p]['hosts'].append(h)
                wholeInventory['all']['children'][p].append(h)
            
            if ("family" in grouping):
                # Create model grouping
                if not (c in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][f]={'hosts':[]}
                    wholeInventory['all']['children'][f]=[]
                # Add device to model group
                #wholeInventory['all']['children'][f]['hosts'].append(h)
                wholeInventory['all']['children'][f].append(h)

            if ("devType" in grouping):
                # Create device type grouping
                if not (c in wholeInventory['all']['children']):
                    #wholeInventory['all']['children'][y]={'hosts':[]}
                    wholeInventory['all']['children'][y]=[]
                # Add device to device type group
                #wholeInventory['all']['children'][y]['hosts'].append(h)
                wholeInventory['all']['children'][y].append(h)

    # Prepare output in correct format
    if (format.upper()=='YAML'):
        output=yaml.dump(wholeInventory)
    elif (format.upper()=='JSON'):
        output=json.dumps(wholeInventory,indent=4)
    else:
        output=''

    # if filename passed, open the file to write to it
    if len(filename)>0:
        f=open(filename,'w')
        
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

def writeAnsibleHostVars (devs, hostName, format, filename='', variables=[]):
    '''
    Function to output hostvars from inventory for specific host in a format suitable for use as an Ansible dynamic inventory
    
    devs = dictionary of devices from getIPFInventory
    hostName = hostname of specific device in inventory
    format = "yaml" or "json"
    filename [optional] = file to output or '' for stdout (default is '')
    variables [optional] = additional hostvars (default is just ansible_host and ansible_connection)
    
    Returns:    True if written OK to file or stdout / False if write failed
    '''
    vars={}
    writeToFile=False
    RetVal=False

    # default set of additional hostvars = empty
    if len(variables)<1:
        variables=[]

    # Loop through passed devices
    for dev in devs:

        # Extract data for inventory
        h=dev['hostname']['data']

        if h.upper()==hostName.upper():
            i=dev['loginIp']
            v=dev['vendor']
            p=dev['platform']
            f=dev['family']
            o=dev['version']
            n=dev['sn']
            c=dev['loginType']
            s=dev['siteName']
            y=dev['devType']
    
            # Assemble hostvars
            vars['ansible_host']=i
            vars['ansible_connection']=c
            for var in variables:
                vars[var]=dev[var]
 
            break
        
    # Prepare output in correct format
    if (format.upper()=='YAML'):
        output=yaml.dump(vars)
    elif (format.upper()=='JSON'):
        output=json.dumps(vars,indent=4)
    else:
        output=''

    # if filename passed, open the file to write to it
    if len(filename)>0:
        f=open(filename,'w')
        
        # write output to file
        try:
            print(output,file=f)
            f.close()
            retVal=True
            pyIPFLog(format.upper()+" format variables successfully written to "+filename)
        except:
            pyIPFLog("Error writing "+format.upper()+ " format variables to "+filename)
    else:
        # write output to stdout
        try:
            print(output)
            retVal=True
            pyIPFLog(format.upper()+" format variables successfully written to stdout")
        except:
            pyIPFLog("Error writing "+format.upper()+ " format variables to stdout")


def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    try:
        devs=getIPFInventory('165.120.82.52:2443','admin','netHero!123')
        if '--list' in opts:
            if len(devs)>0:
                writeAnsibleInventory(devs,'yaml')
        elif '--host' in opts:
            if len(devs)>0:
                writeAnsibleHostVars(devs,args[0],'yaml')
    except:
        pyIPFLog("Parameter error calling getIPFInventory")


if __name__ == "__main__":
    main()