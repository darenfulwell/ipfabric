#!/usr/bin/env python3

'''
Script to test pyIPF module to fetch inventory and write it out as an Ansible inventory
'''

from pyIPF import getIPFInventory, writeAnsibleInventory, pyIPFLog

def main():
    # Run test extraction
    try:
        devs=getIPFInventory('192.168.1.174','admin','netHero!123')
        if len(devs)>0:
            writeAnsibleInventory(devs,'json')
    except:
        pyIPFLog("Parameter error calling getIPFInventory")


if __name__ == "__main__":
    main()