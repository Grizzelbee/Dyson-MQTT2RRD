import paho.mqtt.client as mqtt

HOST = '192.168.1.1'
PORT = 1883
USERNAME = 'NN3-EU-XXXXXXXX'
PASSWORD = 'shortpasswordonmanual'
TOPIC = '475/initialconnection/command'

# TODO get the hashed password with
#TOPIC2 = '475/initialconnection/credentials'
# the anwser will be something like
# {"msg":"DEVICE-CREDENTIALS","time":"2013-01-03T20:26:00.000Z","serialNumber":"NN3-EU-XXXXXXXX","apPasswordHash":"LONGHASHEDPASSWORD"}

PAYLOAD = '{"msg":"JOIN-NETWORK","time":"2016-08-11T14:57:17Z","ssid":"LocalSSID","password":"LocalWiFIPassphrase","requestId":"0123456789ABCDEF"}'
# TODO 
# TODO figure out what if it is usefull
#PAYLOAD = '{"msg":"AUTHORISE-USER-REQUEST","time":"2016-08-11T14:57:17Z","id":"CLOUD_BROKER_USER_ID","requestId":"0123456789ABCDEF"}'
PAYLOAD2 = '{"msg":"CLOSE-ACCESS-POINT","time":"2016-08-11T14:57:17Z"}'

if __name__ == '__main__':
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.connect(HOST, port=PORT, keepalive=60)
    client.publish(TOPIC, PAYLOAD)
    # maybe check the status before sending the next command
    client.publish(TOPIC, PAYLOAD2)
    client.disconnect()
