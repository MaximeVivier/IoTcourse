from simple import MQTTClient
from network import WLAN
import machine
import time
import pycom as pc

pc.heartbeat(False)

# Définition du dictionnaire de couleurs en fontion de leur nom
colors = {
    'vert' : 0x00aa00,
    'rouge' : 0xaa0000,
}

# Fonction à appeler pour changer la couleur de la LED
def changeColor(color):
    hexa = colors[color]
    pc.rgbled(hexa)
    return()

def callback_temp(topic, msg):
    print(msg)

def callback_switch(topic, msg):
    if msg == b"OFF":
        print(msg)
        changeColor('rouge')
    elif msg == b"ON":
        print(msg)
        changeColor('vert')

adc = machine.ADC()
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)

wlan = WLAN(mode=WLAN.STA)
wlan.connect("Freebox-5FB8C7", auth=(WLAN.WPA2, "hispanarum#&-orthodoxi*-ructent-eusebio*"), timeout=5000)

while not wlan.isconnected():
    print("Connecting ...")
    machine.idle()
    time.sleep_ms(500)
print("Connected to WiFi\n")



client_temp = MQTTClient("ordi_max1", "io.adafruit.com",user="adlaffargue", password="aio_uoKY313qNILljZDl1H7765uVtnI5", port=1883)
client_switch = MQTTClient("ordi_max2", "io.adafruit.com",user="adlaffargue", password="aio_uoKY313qNILljZDl1H7765uVtnI5", port=1883)

client_temp.set_callback(callback_temp)
client_temp.connect()
client_temp.subscribe(topic="adlaffargue/feeds/tp-temp")

client_switch.set_callback(callback_switch)
client_switch.connect()
client_switch.subscribe(topic="adlaffargue/feeds/tp-switch")

print("Initialization ok !\n")
while True:
    temp = str(round(apin()/4096*40))
    client_temp.publish(topic="adlaffargue/feeds/tp-temp", msg=temp)
    time.sleep(1)
    client_temp.check_msg()
    client_switch.check_msg()
    time.sleep(1.5)

client_temp.disconnect()
client_switch.disconnect()
