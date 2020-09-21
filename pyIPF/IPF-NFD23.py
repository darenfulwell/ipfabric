#!/usr/bin/env python3

'''
Script to use pyIPF module to fetch IPF data and write it out as rich tables

'''

from pyIPF import getIPFInventory
import sys
import json
import os

def main():
    devs=getIPFInventory('dev13.ipf.ipfabric.io',username='daren',password='darenR0cks',filters={'siteName':['like','L38']})
    writeInventoryTable(devs)

if __name__ == "__main__":
    main()