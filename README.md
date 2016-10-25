Dyson-graph
===========

just a proof of concept and scripts backup for playing with my Dyson Pure Cool Link

# init

to setup the Dyson, you have first to connect on its own WiFI AP and send the SSID and passphrase of your local WiFI
at this point, you can get the hash password when subscribing to the right topic
after than you can ask the dyson do disable its AP and it will connect to your local WiFI

some trial in `Dyson-init.py`

# from MQTT to RRD

Using a modified version of irvined1982/MQTT2RRD as this one expect one sensor value per topic.
Here the Dyson send a json with several sensor or state packed altogether
the script now use paho and python 3

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
