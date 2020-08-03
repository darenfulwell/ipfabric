# pyIPF module

Python module for importing inventory, filtering and exporting detail to other platforms.

## Functions exposed in module

* pyIPFLog (msg):  Function to write a log message using logging module
* fetchIPFAccessToken (IPFServer, userAndPass):  Function to authenticate a user and fetch the token for API calls
* refreshIPFToken (IPFServer, refreshToken):  Function to refresh the access token for API calls
* getIPFData(apiEndpoint, dataHeaders, dataPayload):  Function to fetch arbitrary data from IP Fabric server
* getIPFInventory(IPFServer, username, password, snapshotId, columns, filters):  Function to retrieve IP Fabric inventory details
* writeAnsibleInventory (devices, format, destination, grouping, variables): Function to write Ansible format inventory
* writeAnsibleHostVars (devices, hostName, format, filename, variables): Function to write Ansible format host variables