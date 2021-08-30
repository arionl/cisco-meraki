'''
Meraki Air Marshal AppleTV search

This script searches for Apple TVs within a Meraki organization. It uses a combination of MAC addres prefexies that
are registered to Apple and variations of the name 'Apple TV'. It will likely find more than Apple TVs, but should
surface devices to investigate further.

An optional parameter can be supplied to adjust the timespan (default = 7 days) of historical data to search through.
This script has minimal error checking and potential problem areas are noted ("NOTE:").

This script expects an environmental variable to be set:
MERAKI_DASHBOARD_API_KEY - this needs to be a valid Meraki API key that has at least read-only access
'''

import json
import requests
import os
import argparse
import time

# Create parser for pattern argument
parser = argparse.ArgumentParser(description='Search Apple TVs in Meraki Air Marshal data')

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

        print(" * Working on network '{}'".format(network['name']))

        resp = s.get('https://api.meraki.com/api/v0/networks/{}/devices'.format(network['id']))
        devices = json.loads(resp.text)

        for device in devices:

            if not 'name' in device.keys():
                device['name'] = 'unknown'

            print(" - Working on device '{}'".format(device['name']))

            # NOTE: the 'clients' API endpoint seems wonky and often doesn't return or errors out, so wrap it in a
            # simple retry loop
            response = False
            while not response:
                try:
                    resp = s.get('https://api.meraki.com/api/v0/devices/{}/clients?timespan={}'.format(
                        device['serial'],
                        args.timespan))
                    response = True # Only reached if the above call doesn't throw an exception
                except:
                    print(" ! Error with API, sleeping 2 seconds and trying again")
                    time.sleep(2) # Sleep 2 seconds and try again

            clients = json.loads(resp.text)

            for client in clients:
                if not 'description' in client.keys() or client['description'] == None:
                    client['description'] = 'unknown'

                # NOTE: There's probably a more elegant way of doing this, but since we need to check for two
                # attributes (MAC address and a name match), this is quick and dirty
                if \
                    '5c:f9:38' in client['mac'].lower() or \
                    'f4:b7:e2' in client['mac'].lower() or \
                    '50:32:37' in client['mac'].lower() or \
                    'apple tv' in client['description'].lower() or \
                    'apple-tv' in client['description'].lower() or \
                    'appletv' in client['description'].lower():

                    # NOTE: This could use a CSV writer, but a simple print is sufficient for now
                    print("{},{},{},{},{},{}".format(
                        network['name'],
                        device['name'],
                        client['mac'],
                        client['ip'],
                        client['description'],
                        client['dhcpHostname']))