#!/usr/bin/env python3

"""
Simple Python3 script for retrieving devices from the last snapshot as a Nornir inventory
"""

from nornir import InitNornir
nr = InitNornir(
    core={"num_workers": 10},
    inventory={
        "plugin":"nornir.plugins.inventory.ipfabric.IPFInventory",
        "options": {
            "ssl_verify": False,
            "ipf_url":"https://demo4.ipf.ipfabric.io",
            "ipf_user":"ipfabricdemo",
            "ipf_password":"ipfabricdemo",
        }
    },
    logging={"enabled": False}
)