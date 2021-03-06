import machine
import ubinascii
import pycom, sys, time, network
from umqtt import MQTTClient

wlan = network.WLAN(mode=network.WLAN.STA)

wlan.connect('ssid', auth=(network.WLAN.WPA2, 'password'))

while not wlan.isconnected():
    time.sleep_ms(500)
    print("Wifi .. Connecting")
print("Wifi Connected", wlan.ifconfig())

client_id =  ubinascii.hexlify(machine.unique_id())
BROKER_ADDRESS = '185.216.25.143'
print(client_id)

mqtt_client = MQTTClient(client_id, BROKER_ADDRESS, port=1883)
# print(mqtt_client)
# print(mqtt_client.server)
# print(mqtt_client.port)


def cb(topic, msg):
  print(msg)

mqtt_client.set_callback(cb)
connected = mqtt_client.connect()

for i in range(40):
  mqtt_client.publish(topic='Bin_i', msg='7')
mqtt_client.disconnect()