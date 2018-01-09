import paho.mqtt.client as mqtt
import time, configparser, os
import hashlib, base64
from time import gmtime, strftime
import requests

config = configparser.RawConfigParser()

def get_config_item(section, name, default):
    """
    Gets an item from the config file, setting the default value if not found.
    """
    try:
        value = config.get(section, name)
    except:
        value = default
    return value

def hash_password(password):
    """
    Hash password (in manual and used when connecting on init)
    to a base64 encoded of its shad512 value
    """
    m = hashlib.sha512()
    m.update(str(password).encode('utf-8'))
    return base64.b64encode( m.digest() ).decode('utf-8')

# find why this doesnt works on publisher
def on_connect(client, userdata, flags, respons_code):
    print('status : ' + str(respons_code))

def on_disconnect(client, userdata, respons_code):
    if respons_code != 0:
        print("Unexpected disconnection.")
    print('disconnecting : ' + str(respons_code))
    # TODO put the url in conf
    res = requests.get('https://example.com/sendmsg?msg=Dyson%20Disconnected')
    if res.status_code == 200:
        print('Alert sent')
    else:
        print('got error code:' + res.status_code)

def on_publish(client, userdata, mid):
    print('published : ' + str(mid))

config.read(['/etc/mqtt2rrd.conf', os.path.expanduser('./mqtt2rrd.conf')])


HOST = get_config_item('mqtt','hostname','test.mosquitto.org')
PORT = int(get_config_item('mqtt','port',1883))
USERNAME = get_config_item('mqtt','username','NN3-EU-XXXXXXXX')
PASSWORD = get_config_item('mqtt','password','PASSWORD')
HASHEDPASSWORD = hash_password(PASSWORD)
# TODO use config file
TOPIC = '475/' + USERNAME + '/command'

# TODO write a separate script to change state with
#PAYLOAD = '{"msg":"STATE-SET","time":"2016-08-11T14:57:17Z","data":{"oson":"OFF","fnsp":"0009","nmod":"OFF","fmod":"FAN"}}'

PAYLOAD_state = '{"msg":"REQUEST-CURRENT-STATE","time":"2016-08-11T14:57:17Z"}'
# not needed as sensor data are also returned when requesting current state
#PAYLOAD_sensor = '{"msg":"REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA","time":"2016-08-11T14:57:17Z"}'
# maybe not needed as it seems to be internal counter and data can be found with REQUEST-CURRENT-STATE
#PAYLOAD_usage = '{"msg":"REQUEST-PRODUCT-ENVIRONMENT-AND-USAGE-DATA","time":"2016-08-11T14:57:17Z"}'
# I havent looked at faults meaning
#PAYLOAD = '{"msg":"REQUEST-CURRENT-FAULTS","time":"2016-08-11T14:57:17Z"}'

# TODO daemonize and handle the reconnection
if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, HASHEDPASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_start()
    while True:
        #TODO log
        mytime = strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())
        PAYLOAD_state = '{"msg":"REQUEST-CURRENT-STATE","time":"' + mytime + '"}'
        client.publish(TOPIC, PAYLOAD_state);
        #client.publish(TOPIC, PAYLOAD_sensor);
        #client.publish(TOPIC, PAYLOAD_usage);
        time.sleep(30.0 - (time.time() % 30.0))
    client.disconnect()
