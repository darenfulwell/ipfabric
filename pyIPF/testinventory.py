#!/usr/bin/env python3

'''
Script to test pyIPF module to fetch inventory and write it out as an Ansible inventory
'''

from pyIPF import getIPFInventory, writeAnsibleInventory, writeAnsibleHostVars, pyIPFLog
import sys

def main():
    opts = [opt for opt in sys.argv[1:] if opt.startswith("--")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    
    try:
        devs=getIPFInventory('165.120.82.52:2443','admin','netHero!123')
        if '--list' in opts:
            if len(devs)>0:
                writeAnsibleInventory(devs,'json')
        elif '--host' in opts:
            if len(devs)>0:
                writeAnsibleHostVars(devs,args[0],'json')
    except:
        pyIPFLog("Parameter error calling getIPFInventory")

           


if __name__ == "__main__":
    main()