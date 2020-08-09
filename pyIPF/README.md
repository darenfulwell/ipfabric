# pyIPF.py module

Python 3 module for importing inventory, filtering and exporting detail to other platforms.

## Functions exposed in module

* pyIPFLog (msg):  Function to write a log message using logging module
* fetchIPFAccessToken (IPFServer, userAndPass):  Function to authenticate a user and fetch the token for API calls
* refreshIPFToken (IPFServer, refreshToken):  Function to refresh the access token for API calls
* getIPFData(apiEndpoint, dataHeaders, dataPayload):  Function to fetch arbitrary data from IP Fabric server
* getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):  Function to retrieve IP Fabric inventory details
* writeAnsibleInventory (devices, format, destination, grouping, variables): Function to write Ansible format inventory
* writeAnsibleHostVars (devices, hostName, format, filename, variables): Function to write Ansible format host variables

# IPFAnsible.py script

Python 3 script using pyIPF.py to create dynamic Ansible inventory direct from IP Fabric and write to stdout

## Pre-requisite

Install python-dotenv module

## Parameters

Set environment variables (or create .env in the working directory):

* IPF_SERVER = DNS/IP and port of IP Fabric server
* IPF_USER = API username
* IPF_PASSWORD = API user password
* IPF_FILTER = Filter to apply to inventory - in IP Fabric format {'column':['operator','value']}
* IPF_GROUP = List of categories for groups - "site", "access", "vendor", "platform", "model", "devType" (default is ungrouped)
* IPF_VARS = List of additional host variables (column names)

Command line options:
* --list = produce full Ansible dynamic inventory dictionary
* --host [hostname] = dictionary containing host variables for [hostname]
* --json = output in JSON format (default)
* --yaml = output in YAML format
* --server [IPF Server] = DNS/IP and port of IP Fabric server
* --user [IPF Username] = API username
* --pass [IPF Password] = API user password
* --filter {Filter} = Filter to apply to inventory - in IP Fabric format {'column':['operator','value']}
* --group [Group List] = List of categories for groups - "site", "access", "vendor", "platform", "model", "devType" (default is ungrouped)
* --vars [Var List] = List of additional host variables (column names)