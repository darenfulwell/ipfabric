"""
Python3 function library for testing the IP Fabric's API.
"""
# Built-in/Generic Imports
import requests
# Suppressing SSL certificate warnings if needed
requests.packages.urllib3.disable_warnings()

# Defining main functions
def tokenRequest (tokenServer, userpass):
    authPost = requests.post(tokenServer + 'api/v1/auth/login', json=userpass, verify=False)
    if authPost.ok: print(' User authenticated successfully, TOKEN is ready :)')
    else: print(' User NOT authenticated: ' + str(authPost.reason) + ',  \n  Error: ' + authPost.text)
    return authPost

def refreshToken (refreshServer, refreshToken):
    refreshPost = requests.post(refreshServer + 'api/v1/auth/token', json={'refreshToken': refreshToken}, verify=False)
    if refreshPost.ok: print(' The TOKEN refreshed successfully')
    else: print(' UNABLE to refresh the token: ' + refreshPost.text)
    return refreshPost

def getData(apiEndpoint, dataHeaders, dataPayload):
    dataPost = requests.post(apiEndpoint, headers=dataHeaders, json=dataPayload, verify=False)
    if dataPost.ok: print(' Successfully gathered data from: ' + apiEndpoint)
    else: print(' UNABLE to get data from: ' + apiEndpoint + '\n  Error: ' + dataPost.text)
    return dataPost

def getSeed (getSeedServer, getSeedHeaders):
    seedGet = requests.get(getSeedServer + 'api/v1/settings/seed', headers=getSeedHeaders, verify=False)
    if seedGet.ok: print(' The seed data is: ' + seedGet.text)
    else: print(' UNABLE to get Seed data: '+ seedGet.text)
    return seedGet

def updateSeed(postSeedServer, postSeedHeaders, postSeedLoad):
    seedPost = requests.post(postSeedServer + 'api/v1/settings/seed', headers=postSeedHeaders, json=postSeedLoad, verify=False)
    if seedPost.reason == 'Not Modified': print(' Seed is remaining the same.')
    elif seedPost.ok: print(' Seed updated successfully with: ' + str(postSeedLoad))
    else: print(' UNABLE to update the Seed: ' + seedPost.text)
    return seedPost

def rewriteSeed(putSeedServer, putSeedHeaders, putSeedLoad):
    seedPut = requests.put(putSeedServer + 'api/v1/settings/seed', headers=putSeedHeaders, json=putSeedLoad, verify=False)
    if seedPut.ok: print(' Seed modified successfully with: ' + seedPut.text)
    else: print(' UNABLE to modify Seed: ' + seedPut.text)
    return seedPut

def getSettings(getSettServer, getSettHeaders):
    settingsGet = requests.get(getSettServer + 'api/v1/settings', headers=getSettHeaders, verify=False)
    if settingsGet.ok: print(' Following Settings are in use: ' + settingsGet.text)
    else: print(' UNABLE to get Settings info: ' + settingsGet.text)
    return settingsGet

def getSettingsNet(getSettNetServer, getSettNetHeaders):
    settingsNetGet = requests.get(getSettNetServer + 'api/v1/settings', headers=getSettNetHeaders, verify=False)
    if settingsNetGet.ok: print(' Following Networks in Settings are applied: ' + str(settingsNetGet.json()['networks']))
    else: print(' UNABLE to get Network Settings info: ' + settingsNetGet.text)
    return settingsNetGet

def updateSettings(patchSettServer, patchSettHeaders, patchSettLoad):
    settingsPatch = requests.patch(patchSettServer + 'api/v1/settings', headers=patchSettHeaders, json=patchSettLoad, verify=False)
    if settingsPatch.ok: print(' Settings updated successfully with: ' + str(patchSettLoad))
    else: print(' UNABLE to update Settings: ' + settingsPatch.text)
    return settingsPatch

def startSnapshot(postSnapServer, postSnapHeaders):
    snapshotPost = requests.post(postSnapServer + 'api/v1/snapshots', headers=postSnapHeaders, json={}, verify=False)
    if snapshotPost.ok: print(' New Snapshot started successfully')
    else: print(' UNABLE to start Snapshot: ' + snapshotPost.text)
    return snapshotPost

def getSnapshot(getSnapServer, getSnapHeaders):
    snapshotGet = requests.get(getSnapServer + 'api/v1/snapshots', headers=getSnapHeaders, verify=False)
    if snapshotGet.ok: print(' The total number of available Snapshots is: ' + str(len(snapshotGet.json())))
    else: print(' UNABLE to get snapshot information: ' + snapshotGet.text)
    return snapshotGet

def e2ePath(e2eQuerry, e2eHeaders):
    e2eGet = requests.get(e2eQuerry, headers=e2eHeaders, verify=False)
    if e2eGet.ok: print(' The E2E path simulation is ready.')
    else: print(' UNABLE to simulate E2E: ' + e2eGet.text)
    return e2eGet
