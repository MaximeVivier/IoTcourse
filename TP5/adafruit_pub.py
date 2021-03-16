from simple import MQTTClient
from network import WLAN
import machine
import time
import pycom as pc

pc.heartbeat(False)

# ------------------  Définition du dictionnaire de couleurs en fontion de leur nom  ------------------------------
colors = {
    'vert' : 0x00aa00,
    'rouge' : 0xaa0000,
}
# -------------------------------------------------------------------------------------------------------------------



# ---------------------  Fonction à appeler pour changer la couleur de la LED  ------------------------------------
def changeColor(color):
    hexa = colors[color]
    pc.rgbled(hexa)
    return()
# -------------------------------------------------------------------------------------------------------------------



# ---------------  Le callback pour le feed de température affiche la température  ----------------------------------
def callback_temp(topic, msg):
    print(msg)
# -------------------------------------------------------------------------------------------------------------------



# ---------  Le callback pour le feed de switch change la couleur en fonction de la valeur envoyée ON ou OFF  ---------
def callback_switch(topic, msg):
    if msg == b"OFF":
        print(msg)
        changeColor('rouge')
    elif msg == b"ON":
        print(msg)
        changeColor('vert')
# -------------------------------------------------------------------------------------------------------------------



# ------  Initialisation des pins numériques avec le protocol I2C pour avoir les valeurs du capteur de température  ------
resolution_temp = 0.0625 # Définition de la résolution du capteur de température

i2c = machine.I2C(0, pins=('P9','P10'))
i2c.init(machine.I2C.MASTER, baudrate=20000)
scan = i2c.scan()[0] # contient l'adresse du capteur
# -------------------------------------------------------------------------------------------------------------------

## ---------------   Initialisation du pin analogique pour avoir les valeurs du potar  -----------------------------
## Partie non utilisée pour run le code avec le capteur de température
# adc = machine.ADC()
# apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)
# -------------------------------------------------------------------------------------------------------------------


# --------------------------------  Connection au WIFI  ------------------------------------------------------------
wlan = WLAN(mode=WLAN.STA)
wlan.connect("Freebox-5FB8C7", auth=(WLAN.WPA2, "hispanarum#&-orthodoxi*-ructent-eusebio*"), timeout=5000)

while not wlan.isconnected():
    print("Connecting ...")
    machine.idle()
    time.sleep_ms(500)
print("Connected to WiFi\n")
# -------------------------------------------------------------------------------------------------------------------


# --------------------------------  Crétaion des clients liés aux feeds  ------------------------------------------------------------

# On aurait pu créer qu'un client, envoyer des données avec celui-ci et souscrire au switch avec le même.
# On a préféré avoir deux instances de client pour souscrire aux deux feeds simultanément et avoir les données de température et
# et de switch qui sont envoyées sur Adafruit.

client_temp = MQTTClient("ID_machine1", "io.adafruit.com",user="Username", password="API-key_in_my_Keys", port=1883)
client_switch = MQTTClient("ID_machine2", "io.adafruit.com",user="Username", password="API-key_in_my_Keys", port=1883)

client_temp.set_callback(callback_temp)
client_temp.connect()
client_temp.subscribe(topic="adlaffargue/feeds/tp-temp")

client_switch.set_callback(callback_switch)
client_switch.connect()
client_switch.subscribe(topic="adlaffargue/feeds/tp-switch")
# ------------------------------------------------------------------------------------------------------------------------------------

def lecture_température_depuis_trame(MSB, LSB):
    # [MSB,LSB] = i2c.readfrom(scan,2) # On lit la derniere valeur dans le registre du capteur
    output_hex = hex(MSB) + hex(LSB)[2] # on se débarasse des 4 derniers bits du LSB
    output_dec = int(output_hex)
    temp = str(output_dec * resolution_temp)
    return(temp)

# --------------  Acquisition température, envoie température et check messages de températures et switch  ----------------------

print("Initialization ok !\n")
while True:

    # Lecture
    [MSB,LSB] = i2c.readfrom(scan,2)
    temperature = lecture_température_depuis_trame(MSB,LSB)

    # temp = str(round(apin()/4096*40)) # lecture de la valeur du potar pour les premiers essais

    # Envoie de la température sur le feed Adafruit
    client_temp.publish(topic="adlaffargue/feeds/tp-temp", msg=temperature)

    time.sleep(1)

    # Récupère les données disponibles envoyées par les feeds
    client_temp.check_msg()
    # Le callback défini dans le client s'occupe de changer la couleur en fonction de la valeur reçues
    client_switch.check_msg()
    time.sleep(1.5)
# ------------------------------------------------------------------------------------------------------------------------------------


# --------------  Déconnecter les clients  ----------------------
client_temp.disconnect()
client_switch.disconnect()
# ---------------------------------------------------------------
