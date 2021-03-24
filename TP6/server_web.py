# Maxime VIVIER
# Adrien LAFFARGUE
import machine
import pycom, sys, time, network, usocket
import pycom as pc


# Désactiver le clignotment de la LED du au fonctionnement classique de la pycom
pc.heartbeat(False)

# Initialiser la lecture du de données I2C
adc = machine.ADC()
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)


def client_connect(clientsocket):
    r = clientsocket.recv(4096)
    if len(r) == 0:
        clientsocket.close()
        return
    else:
        # Quand une requête est reçue on l'affiche
        print("Received: {}".format(str(r)))
    
    # On mesure la tension renvoyée par le potar
    val = apin()
    tension = str(val*3.3/4096)[:3]
    # On créé les headers et le body de la réponse qui est simplement une page HTML avec la map
    # Le body HTML contient la donnée de tension mesurée précédemment
    http = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n"
    mapGPS =  '<!DOCTYPE html><html manifest="site.manifest"><head><meta charset="utf-8"><title>Serveur web</title></head><style>body {hight: 100%;} div {display: flex;flex-direction: column;align-items: center;}</style><body><div id="main"><h1>Lopy server</h1><p>Tension ' + tension + ' V</p></div></body></html>'
    # Si la requête faite est une méthode GET, on renvoie la concaténation des headers et du body
    if "GET / " in str(r):
        clientsocket.send(http + mapGPS)
    
    # Une fois les données renvoyées on ferme la socket
    clientsocket.close()


# Connection au réseau WIFI en spécifiant le SSID et le mot de passe
wlan = network.WLAN(mode=network.WLAN.STA)

wlan.connect('Freebox-5FB8C7', auth=(network.WLAN.WPA2, 'hispanarum#&-orthodoxi*-ructent-eusebio*'))

while not wlan.isconnected():
    time.sleep_ms(500)
    print("Wifi .. Connecting")
print("Wifi Connected", wlan.ifconfig())

# Une fois connecté au WIFI, on créé une socket
s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
print("s", s)

# On lie la socket à l'adresse IP de la pycom sur le réseau sur le port 8080
s.bind((wlan.ifconfig()[0], 8080))

s.listen(1)

while True:
    (clientsocket, address) = s.accept()
    client_connect(clientsocket)
    print('ok')

s.close()
