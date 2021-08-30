airmarshal.py
=============

This script searches for patterns of SSIDs from Air Marshal data. It expects a single command line option that is the SSID pattern to search for. Please see the script for additional details.

If you run the script like this:

`MERAKI_DASHBOARD_API_KEY=SOMEAPIKEY python3 airmarshal.py -t 2678400 impala`

..you should see outcome like this:

```
SOMENETWORK,Dons Impala
SOMENETWORK,rashadimpala
SOMENETWORK,stevenimpala
SOMENETWORK,Impala2016
SOMENETWORK,impala
SOMENETWORK,Smith Impala
SOMENETWORK,Greyimpala
SOMENETWORK,Impala Wifi
SOMENETWORK,donimpala
SOMENETWORK,Carl Impala
```

(it's quite impressive how many Chevy Impalas are out there with built-in Wifi)

appletvs.py
============

This script searches for Apple TV devices attached to Meraki APs. Please see the script for additional details.

If you run the script like this:

`MERAKI_DASHBOARD_API_KEY=SOMEAPIKEY python3 appletvs.py`

..you should see outcome like this:

```
 * Working on network 'SOMENETWORK'
 - Working on device 'SOMEAP01'
SOMENETWORK,SOMEAP01,50:32:37:XX:XX:XX,172.18.216.113,Apple-TV,Apple-TV
```