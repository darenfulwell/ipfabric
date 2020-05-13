"""
Simple Python3 script for changing IP Fabric settins and starting snapshots over API
"""
# Built-in/Generic Imports
from ipfapi import *

# Starting with variables
server = 'https://server/'
authData = { 'username': 'username', 'password' : 'password' }

# Working with tokens and creating headers
tokens = tokenRequest(server, authData).json()
headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}

# Refreshing the token if needed
# newTokens = refreshToken(server, tokens['refreshToken']).json()
# newHeaders = { 'Authorization' : 'Bearer ' + newTokens['accessToken'], 'Content-Type': 'application/json'}

# Defining API payloads for testing
paySeed1 = []
paySeed2 = ['10.113.1.8', '10.113.201.10', '10.113.101.36'] # List of IP Addresses to include to the seed
paySettings1 = {"networks": {"exclude": [], "include": ['10.66.255.105/32', '10.66.255.110/32']}}
paySettings2 = {"networks": {"exclude": [], "include": ["198.18.0.0/24"]}}

# Main functions for testing in the console
a = getSeed(server, headers)
b = updateSeed(server, headers, paySeed2)
c = rewriteSeed(server, headers, paySeed1)
d = getSettings(server, headers)
e = getSettingsNet(server, headers)
f = updateSettings(server, headers, paySettings1)
g = getSnapshot(server, headers)
s = startSnapshot(server, headers)
