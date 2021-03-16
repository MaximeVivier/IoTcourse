from simple import MQTTClient
from network import WLAN
import machine
import time

def sub_cb(topic, msg):
   print(msg)

adc = machine.ADC()
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)

wlan = WLAN(mode=WLAN.STA)
wlan.connect("Freebox-5FB8C7", auth=(WLAN.WPA2, "hispanarum#&-orthodoxi*-ructent-eusebio*"), timeout=5000)

while not wlan.isconnected():
    print("Connecting ...")
    machine.idle()
print("Connected to WiFi\n")

client = MQTTClient("ordi_adrien", "io.adafruit.com",user="adlaffargue", password="aio_eaGs44EvuauZdrbBiFee7o0fisJ8", port=1883)

client.set_callback(sub_cb)
client.connect()
client.subscribe(topic="adlaffargue/feeds/tp-iot-mqtt")

while True:
    temp = str(round(apin()/4096*40))
    client.publish(topic="adlaffargue/feeds/tp-iot-mqtt", msg=temp)
    time.sleep(1)
    client.check_msg()
    time.sleep(1.5)

client.disconnect()
