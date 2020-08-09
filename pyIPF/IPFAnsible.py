#!/usr/bin/env python3

'''
Script to use pyIPF module to fetch inventory and write it to stdout as an Ansible inventory

Set environment variables - (or create .env in the working directory - requires 'dotenv' to be installed):

IPF_SERVER = DNS/IP and port of IP Fabric server
IPF_USER = API username
IPF_PASSWORD = API user password
IPF_FILTER = Filter to apply to inventory - in IP Fabric format {'column':['operator','value']}
IPF_GROUP = List of categories for groups - "site", "access", "vendor", "platform", "model", "devType" (default is ungrouped)
IPF_VARS = List of additional host variables (column names)

Command line options:
--list = produce full Ansible dynamic inventory dictionary
--host [hostname] = dictionary containing host variables for [hostname]
--yaml = switch to YAML format
--server [IPF Server] = DNS/IP and port of IP Fabric server
--user [IPF Username] = API username
--pass [IPF Password]= API user password
--filter {Filter} = Filter to apply to inventory - in IP Fabric format {'column':['operator','value']}
--group [Group List] = List of categories for groups - "site", "access", "vendor", "platform", "model", "devType" (default is ungrouped)
--vars [Var List] = List of additional host variables (column names)

'''

from pyIPF import getIPFInventory, writeAnsibleInventory, writeAnsibleHostVars, pyIPFLog
import sys
import json
import os
from dotenv import load_dotenv

def main():
    # fetch options and arguments before processing

    IPFServer = ''
    IPFUser = ''
    IPFPassword = ''
    IPFGrouping = ''
    IPFVars = ''
    IPFFilter = ''
    devUsername = ''
    devPassword = ''

    format="json"
    writeInv=False
    writeVars=False
    excRaised=False
    index=1
    for opt in sys.argv[1:]:
        if ("-yaml" in opt):
            format="yaml"
        elif ("--list" in opt):
            writeInv=True
        elif ("--host" in opt):
            writeVars=True
            try:
                hostName=sys.argv[index+1]
            except:
                excRaised=True
                print("No hostname specified")
        elif ("--serv" in opt):
            try:
                IPFServer=sys.argv[index+1]
            except:
                excRaised=True
                print("No server specified")
        elif ("--user" in opt):
            try:
                IPFUser=sys.argv[index+1]
            except:
                excRaised=True
                print("No username specified")
        elif ("--pass" in opt):
            try:
                IPFPassword=sys.argv[index+1]
            except:
                excRaised=True
                print("No password specified")
        elif ("--vars" in opt):
            try:
                IPFVars=sys.argv[index+1]
            except:
                excRaised=True
                print("No Variables specified")
        elif ("--group" in opt):
            try:
                IPFGrouping=sys.argv[index+1]
            except:
                excRaised=True
                print("No grouping specified")
        elif ("--filt" in opt):
            try:
                IPFFilter=sys.argv[index+1]
            except:
                excRaised=True
                print("No filter specified")
        elif ("--sshuser" in opt):
            try:
                devUsername=sys.argv[index+1]
            except:
                excRaised=True
                print("No SSH username specified")
        elif ("--sshpass" in opt):
            try:
                devPassword=sys.argv[index+1]
            except:
                excRaised=True
                print("No SSH password specified")
        index+=1

    # Load .env if present to refer to if environment variables not set
    load_dotenv()

    # If command line parameters not present, pick out environment variable values
    if not IPFServer:
        IPFServer = os.getenv('IPF_SERVER')
    if not IPFUser:
        IPFUser = os.getenv('IPF_USER')
    if not IPFPassword:
        IPFPassword = os.getenv('IPF_PASSWORD')
    if not IPFGrouping:
        IPFGrouping = os.getenv('IPF_GROUP')
    if not IPFVars:
        IPFVars = os.getenv('IPF_VARS')
    if not IPFFilter:
        IPFFilter = os.getenv('IPF_FILTER')
    if not devUsername:
        devUsername = os.getenv('IPF_SSH_USER')
    if not devPassword:
        devPassword = os.getenv('IPF_SSH_PASS')

    # Translate strings for grouping, variables and filter to lists and dictionary
    if IPFGrouping:
        IPFGrouping=IPFGrouping.strip("[]").replace('"','').replace('\'','').split(',')
        if IPFGrouping==['']: IPFGrouping=[]
    else:
        IPFGrouping=[]

    if IPFVars:
        IPFVars=IPFVars.strip("[]").replace('"','').replace('\'','').split(',')
    else:
        IPFVars=[]

    if IPFFilter:
        f=json.loads(IPFFilter.replace("'","\""))
        IPFFilter=f
    else:
        IPFFilter={}

    # Pull data and write it in the right format
    try:
        if not excRaised and (writeInv or writeVars) and len(IPFServer)>0 and len(IPFUser)>0 and len(IPFPassword)>0:
            try:
                devs=getIPFInventory(IPFServer,IPFUser,IPFPassword,filters=IPFFilter)
                if writeInv:
                    if len(devs)>0:
                        writeAnsibleInventory(devs,format,sshUser=devUsername,sshPass=devPassword,grouping=IPFGrouping,variables=IPFVars)
                elif writeVars:
                    if len(devs)>0:
                        writeAnsibleHostVars(devs,args[0],format,variables=IPFVars)
            except:
                print("Inventory retrieval failed")
        else:
            print("Missing --list, --host, --server, --user or --password")
    except:
        print("No valid server, username or password")

if __name__ == "__main__":
    main()