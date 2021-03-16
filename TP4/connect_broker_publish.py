import machine
import ubinascii
import pycom, sys, time, network
from simple import MQTTClient

# --------------------------------  Connection au WIFI  ------------------------------------------------------------
wlan = network.WLAN(mode=network.WLAN.STA)

wlan.connect('Freebox-5FB8C7', auth=(network.WLAN.WPA2, 'hispanarum#&-orthodoxi*-ructent-eusebio*'))

while not wlan.isconnected():
    time.sleep_ms(500)
    print("Wifi .. Connecting")
print("Wifi Connected", wlan.ifconfig())
# -------------------------------------------------------------------------------------------------------------------


# ----------------  Initialisation des pins analogiques pour acquérir les données du potar  -------------------------
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)
# -------------------------------------------------------------------------------------------------------------------


# --------------------------  Initialisation du client MQTT  --------------------------------------------------------
client_id =  ubinascii.hexlify(machine.unique_id())
BROKER_ADDRESS = '185.216.25.143'

mqtt_client = MQTTClient(client_id, BROKER_ADDRESS, port=1883)
# -------------------------------------------------------------------------------------------------------------------


# -------------------------  Configuration de la connexion MQTT  ----------------------------------------------------
def cb(topic, msg):
  print(msg)

mqtt_client.set_callback(cb)
connected = mqtt_client.connect()
mqtt_client.subscribe('lefoot')
# -------------------------------------------------------------------------------------------------------------------



# ----------  Acquisition de la donnée du potar ensuite envoyée au broker (toutes les secondes)  --------------------
while True:
    val = round(apin()*40/4096)
    mqtt_client.publish(topic='temp', msg=str(val))
    print(val)
    time.sleep(1)
# -------------------------------------------------------------------------------------------------------------------
