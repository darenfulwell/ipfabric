#!/usr/bin/env python3

'''
Script to test pyIPF module to fetch inventory and write it out as an Ansible inventory

Set environment variables:

IPF_SERVER = DNS/IP and port of IP Fabric server
IPF_USER = API username
IPF_PASSWORD = API user password
'''

from pyIPF import getIPFInventory, writeAnsibleInventory, writeAnsibleHostVars, pyIPFLog
import sys
import os

def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    IPFServer = ''
    IPFUser = ''
    IPFPassword = ''
    IPFGrouping = ''
    IPFVars = ''
    IPFFilter = ''

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
                pyIPFLog("No hostname specified on command line")
                break
        elif ("--server" in opt):
            try:
                IPFServer=sys.argv[index+1]
            except:
                excRaised=True
                print("No server specified")
                pyIPFLog("No server specified on command line")
                break
        elif ("--user" in opt):
            try:
                IPFUser=sys.argv[index+1]
            except:
                excRaised=True
                print("No username specified")
                pyIPFLog("No username specified on command line")
                break
        elif ("--pass" in opt):
            try:
                IPFPassword=sys.argv[index+1]
            except:
                excRaised=True
                print("No password specified")
                pyIPFLog("No password specified on command line")
                break
        elif ("--vars" in opt):
            try:
                IPFVars=sys.argv[index+1]
            except:
                excRaised=True
                print("No Variables specified")
                pyIPFLog("No variables specified on command line")
                break
        elif ("--group" in opt):
            try:
                IPFGrouping=sys.argv[index+1]
            except:
                excRaised=True
                print("No grouping specified")
                pyIPFLog("No grouping specified on command line")
                break
        elif ("--filter" in opt):
            try:
                IPFFilter=sys.argv[index+1]
            except:
                excRaised=True
                print("No filter specified")
                pyIPFLog("No filter specified on command line")
                break
        index+=1

    if not IPFServer:
        IPFServer = os.getenv('IPF_SERVER')
    if not IPFUser:
        IPFUser = os.getenv('IPF_USER')
    if not IPFPassword:
        IPFPassword = os.getenv('IPF_PASSWORD')
    if not IPFGrouping:
        IPFGrouping = os.getenv('IPF_GROUPING')
    if not IPFVars:
        IPFVars = os.getenv('IPF_VARS')
    if not IPFFilter:
        IPFFilter = os.getenv('IPF_FILTER')

    try:
        if not excRaised and (writeInv or writeVars) and len(IPFServer)>0 and len(IPFUser)>0 and len(IPFPassword)>0:
            try:
                devs=getIPFInventory(IPFServer,IPFUser,IPFPassword)
                if writeInv:
                    if len(devs)>0:
                        writeAnsibleInventory(devs,format)
                elif writeVars:
                    if len(devs)>0:
                        writeAnsibleHostVars(devs,args[0],format)
            except:
                pyIPFLog("Parameter error calling getIPFInventory")
    except:
        pyIPFLog("No valid server, username or password")

if __name__ == "__main__":
    main()