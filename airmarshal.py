'''
Meraki Air Marshal SSID Search

This script searches for patterns of SSIDs from Air Marshal data. It expects a single command line argument that is
the SSID pattern to search for. SSIDs containing this pattern will be returned. The pattern is used with
're.matchall()' so a regular expression can be specified. The pattern will be treated as case-insensitive through the
use of 're.IGNORECASE'. An optional parameter can be supplied to adjust the timespan (default = 7 days) of historical
data to search through. This script has minimal error checking and potential problem areas are noted ("NOTE:").
Network calls via the 'requests' module ARE NOT wrapped in 'try' blocks to catch exceptions.

This script expects an environmental variable to be set:
MERAKI_DASHBOARD_API_KEY - this needs to be a valid Meraki API key that has at least read-only access
'''

import json
import requests
import os
import argparse
import re

# Create parser for pattern argument
parser = argparse.ArgumentParser(description='Search for a pattern in Meraki Air Marshal SSID names')

# Add argument to the parser
parser.add_argument("pattern")

parser.add_argument('--timespan', '-t',
                    dest='timespan', type=int,
                    default=(60*60*24*7), # 7 days in seconds
                    help='The value must be in seconds and be less than or equal to 31 days. The default is 7 days.')

# Parse the arguments
args = parser.parse_args()

# Check to see if a timespan > the Meraki allowed limit (31 days) has been specified
if args.timespan > (60*60*24*31):
    print("ERROR: Meraki Air Marshal API only allows timespan of <= 31 days")
    exit()

with requests.Session() as s:
    s.headers.update({'X-Cisco-Meraki-API-Key': '{}'.format(os.environ['MERAKI_DASHBOARD_API_KEY']),
                      'Content-Type':'application/json'})

    # Get the organization ID(s)
    resp = s.get('https://api.meraki.com/api/v0/organizations')
    if resp.status_code != 200:
        print("API ERROR: Can't request Organizations!")
        exit()

    # NOTE: Assuming only 1 organization ID so only using the data from the first array element
    org_id = json.loads(resp.text)[0]['id']

    # Pass in the org ID and the response data is an array of all networks in the Meraki environment
    resp = s.get('https://api.meraki.com/api/v0/organizations/{}/networks'.format(org_id))
    if resp.status_code != 200:
        print("API ERROR: Can't request Networks!")
        exit()

    networks = json.loads(resp.text)

    # Iterate through all of the networks returned
    for network in networks:

        # Ignore networks that aren't wireless (i.e., MX device or camera networks)
        if not network['type'] == 'wireless':
            continue

        # Pass in the network ID and the timespan and get an array of Air Marshal data back
        resp = s.get('https://api.meraki.com/api/v0/networks/{}/airMarshal?timespan={}'.format(network['id'],
                                                                                               args.timespan))
        if resp.status_code != 200:
            print("API ERROR: Can't request network {} - {}".format(network['id'],network['name']))
            continue

        airmarshal = json.loads(resp.text)

        # Iterate through all of the Air Marshal data
        for record in airmarshal:

            # Check for any SSID matches the specific pattern
            if re.findall(args.pattern, record['ssid'], flags=re.IGNORECASE):
                print('{},{}'.format(network['name'],record['ssid']))
