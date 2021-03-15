import machine
from machine import I2C
import pycom, sys, time, network, usocket
from umqtt import MQTTClient

"""--------------------------- WiFi connection -------------------------------------------"""
# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)
#### MPD EFFACER -----------------------------------------------------------------------------------------
wlan.connect('Freebox-5FB8C7', auth=(network.WLAN.WPA2, 'hispanarum#&-orthodoxi*-ructent-eusebio*'))
#### MPD EFFACER -----------------------------------------------------------------------------------------
while not wlan.isconnected():
    time.sleep_ms(500)
    print("Wifi .. Connecting")
print("Wifi Connected", wlan.ifconfig())


"""----------------------------------- Sockey setup ------------------------------------------"""
#s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
#print("s", s)
#s.bind((wlan.ifconfig()[0], 8080))
#s.listen(1)

"""------------------------------------ machine ID -------------------------------------------"""
machineID = machine.unique_id()
BROKER_ADDRESS = '185.216.25.143'
pycom_mqtt_client = MQQTClient(machineID,BROKER_ADDRESS,port=1883)

def cb(topic,message):
    print(message)

pycom_mqtt_client.set_callback(cb)
pycom_mqtt_client.connect()
