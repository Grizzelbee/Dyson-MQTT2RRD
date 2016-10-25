import paho.mqtt.client as mqtt
import time
starttime=time.time()

# TODO use config file
HOST = 'test.mosquitto.org'
PORT = 1883
USERNAME = 'NN3-EU-XXXXXXXX'
PASSWORD = 'LONGHASHEDPASSWORD'
TOPIC = '475/' + USERNAME + '/command'

# TODO write a separate script to change state with
#PAYLOAD = '{"msg":"STATE-SET","time":"2016-08-11T14:57:17Z","data":{"oson":"OFF","fnsp":"0009","nmod":"OFF","fmod":"FAN"}}'

PAYLOAD_state = '{"msg":"REQUEST-CURRENT-STATE","time":"2016-08-11T14:57:17Z"}'
PAYLOAD_sensor = '{"msg":"REQUEST-PRODUCT-ENVIRONMENT-CURRENT-SENSOR-DATA","time":"2016-08-11T14:57:17Z"}'
# maybe not needed as it seems to be internal counter and data can be found with REQUEST-CURRENT-STATE
PAYLOAD_usage = '{"msg":"REQUEST-PRODUCT-ENVIRONMENT-AND-USAGE-DATA","time":"2016-08-11T14:57:17Z"}'
# I havent looked at faults meaning
#PAYLOAD = '{"msg":"REQUEST-CURRENT-FAULTS","time":"2016-08-11T14:57:17Z"}'

# TODO daemonize
if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(HOST, port=PORT, keepalive=60)
    while True:
        client.publish(TOPIC, PAYLOAD_state);
        client.publish(TOPIC, PAYLOAD_sensor);
        client.publish(TOPIC, PAYLOAD_usage);
        time.sleep(30.0 - ((time.time() - starttime) % 30.0))
    client.disconnect()
