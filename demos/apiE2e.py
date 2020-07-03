"""
Simple Python3 scriptlet for testing E2E over API in the IP Fabric platform.
"""
# Built-in/Generic Imports
from ipfapidemo import tokenRequest, e2ePath
# Basic variables
server = 'https://server/'
authData = { 'username': 'username', 'password' : 'password' }
tokens = tokenRequest(server, authData).json()
headers = { 'Authorization' : 'Bearer ' + tokens['accessToken'], 'Content-Type': 'application/json'}

# Basic E2E path parameters
e2eParams = {
    'e2eEndpoint' : server + 'api/v1/graph/end-to-end-path',
    'sourceIP' : '?source=' + 'xx.xx.xx.xx',
    'destinationIP' : '&destination=' + 'xx.xx.xx.xx',
    'sourcePort' : '&sourcePort=' + '10000',
    'destinationPort' : '&destinationPort=' + 'xx',
    'asymetricOption' : '&asymmetric=' + 'false',
    'rpfOption' : '&rpf=' + 'true',
    'protocolType' : '&protocol=' + 'tcp',
    'snapshotID' : '&snapshot=' + 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
}

# E2E path querry definition
e2eQuerry = ''
for val in e2eParams.values(): e2eQuerry += val

# Running the End to End path simulation in the console
e = e2ePath(e2eQuerry, headers)
