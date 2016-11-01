Dyson-graph
===========

just a proof of concept and scripts backup for playing with my Dyson Pure Cool Link

# init

to setup the Dyson, you have first to connect on its own Wi-Fi APi. The Fan will
broadcast on Bonjour a service of type *_dyson_mqtt._tcp* listening on port
1883 (and in my case on address 192.168.1.1). You have to init the fan by
sending SSID and passphrase of your local Wi-Fi. after than you can ask the
dyson do disable its AP and it will connect to your local Wi-Fi.
From this point, the fan will try to connect to Dyson/Amazon server to send data.

some trial in `Dyson-init.py`

took some example from http://aakira.hatenablog.com/entry/2016/08/12/012654

After this initialization, you'll have to use the hashed password to connect to
the fan. The hashed password is a base64 encoded of the sha512 of the password
written on manual and on the fan label

# from MQTT to RRD

Using a modified version of irvined1982/MQTT2RRD as this one expect one sensor
value per topic.  Here the Dyson send a json with several sensor or state
packed altogether the script now use paho and python 3

`mqtt2rrd.py` with `mqtt2rrd.conf.example`

that will create a lot of rrd files

# requesting to send sensor data

If not doing anything, the Fan does not send data to subscriber, you need to publish some command at fixed interval (here every 30 seconds as the pure link app does)

I'm currently using `Dyson-requester.py` in a screen

# RRD to graph

to create graph, I'm using rrd.cgi
http://haroon.sis.utoronto.ca/rrd/scripts/
with the conf `rrd.cfg`

some graphs can be removed as they are redundant

# Data explanation

## CURRENT-STATE

### product-state

| name | meaning | possible values |
| ------------- | ----- | ----- |
| ercd | ? | NONE , or some hexa values |
| filf | Filter life remaining (hour) | 0000 - 4300 |
| fmod | Mode | FAN , AUTO |
| fnsp | Fan speed | 0001 - 0010, AUTO |
| fnst | Fan Status | ON , OFF |
| nmod | Night mode | ON , OFF |
| oson | Oscillation | ON , OFF |
| qtar | Air Quality target | 0001 , 0003... |
| rhtm | Collect Data ? | OFF... |
| wacd | ? | NONE... |

### scheduler

| name | meaning | possible values |
| ------------- | ----- | ----- |
| dstv | ? | 0001... |
| srsc | ? | 7c68... |
| tzid | timezone? | 0001... |

## ENVIRONMENTAL-CURRENT-SENSOR-DATA

### data

| name | meaning | possible values |
| ------------- | ----- | ----- |
| hact | Humidity (%) | 0000 - 0100 |
| pact | Dust | 0000 - 0009 |
| sltm | Sleep Timer | OFF... 9999 |
| tact | Temperature in Kelvin | 0000 - 5000 |
| vact | volatil organic compounds | 0001 - 0009 |

## ENVIRONMENTAL-AND-USAGE-DATA

Redundent values ?

### data

| name | meaning | possible values |
| ------------- | ----- | ----- |
| pal0 - pal9 | number of second spend in this level of dust since the begining of hour | 0000 - 3600 |
| palm | seems to be a median value of palX |  |
| vol0 - vol9 | number of second spend in this level of voc since the begining of hour | 0000 - 3600 |
| volm | seems to be a median value of volX |  |
| aql0 - aql9 | number of second spend in this level of air quality | max (pal, vol)) since the begining of hour | 0000 - 3600 |
| aqlm | seems to be a median value of aqlX |  |
| fafs | seems to be a number of seconds spend in a specific time | 0000 - 3600 |
| faos | seems to be a number of seconds spend in a specific time | 0000 - 3600 |
| fofs | seems to be a number of seconds spend in a specific time | 0000 - 3600 |
| fons | seems to be a number of seconds spend in a specific time | 0000 - 3600 |
| humm | humidity ? (%) | 0000 - 0100 |
| tmpm | temperature in kelvin ? | 0000 - 5000 |

