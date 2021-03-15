import machine
from machine import I2C
import pycom, sys, time, network, usocket



"""-------------------------------------Socket functions----------------------------------------------"""

def client_connect(clientsocket, latitude, longitude):
    r = clientsocket.recv(4096)
    if len(r) == 0:
        clientsocket.close()
        return
    else:
        # Quand une requête est reçue on l'affiche
        print("Received: {}".format(str(r)))

    # On créé les headers et le body de la réponse qui est simplement une page HTML avec la map
    # Le body HTML contient les données de latitude et longitude obtenues au préalable avec le capteur GPS
    http = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n"
    mapGPS =  '<html><head><meta charset="utf-8"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.1/dist/leaflet.css" integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==" crossorigin="" /><style type="text/css">#map{height:400px;}</style><title>Carte</title></head><body><div id="map"></div><script src="https://unpkg.com/leaflet@1.3.1/dist/leaflet.js" integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw==" crossorigin=""></script><script type="text/javascript">var lat =' + str(latitude) + ';var lon =' +str(longitude)+';var macarte = null;function initMap() {macarte = L.map(\'map\').setView([lat, lon], 11);L.tileLayer(\'https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png\', {attribution: \'données © <a href="//osm.org/copyright">OpenStreetMap</a>/ODbL - rendu <a href="//openstreetmap.fr">OSM France</a>\',minZoom: 1,maxZoom: 20}).addTo(macarte);var marker = L.marker([lat, lon]).addTo(macarte);}window.onload = function(){initMap(); };</script></body></html>'

    # Si la requête faite est une méthode GET, on renvoie la concaténation des headers et du body
    if "GET / " in str(r):
        clientsocket.send(http + mapGPS)
    
    # Une fois les données renvoyées on ferme la socket
    clientsocket.close()

"""-------------------------------------GPS functions-------------------------------------------------"""

def read_byte(add):
    return i2c.readfrom(add,255).decode()

def read_msg(frame):
    # Initialisation de la liste de messages
    messages = []
    
    # Initialisation de l'index de fin de la première donnée
    idx_end_of_incomplete_beginning = frame.find('\r\n')

    if idx_end_of_incomplete_beginning == -1:
        # Si la trame est vide on arrête la fonction ici
        return()

    else:
        # Récupère le message incomplet au début de la trame
        incomplete_beginning = frame[:idx_end_of_incomplete_beginning]
        frame = frame[idx_end_of_incomplete_beginning:]

        # Identification de la première trame complète
        idx_begin = frame.find('$')
        idx_end = frame.find('\r\n')

        # teste s'il reste des messages complets dans la trame autre que ce qui est incomplet au début
        messages_remaining = (idx_begin !=-1 and idx_begin != -1)

        while messages_remaining:
            # Ajoute le message complet à la liste de message
            messages.append(frame[idx_begin+1:idx_end])

            # Les données sont séparées par 2 caractères \r\n
            # On regarde maintenant le reste de la trame
            # Et on refait la même chose
            frame = frame[idx_end+2:]                                   # retire le message de la trame initiale
            idx_begin = frame.find('$')
            idx_end = frame.find('\r\n')
            messages_remaining = (idx_begin !=-1 and idx_begin != -1)   # teste s'il y a un nouveau message complet qui arrive

        # Quand il n'y a plus de message complet dans la trame on renvoie None si elle est vide
        # Ou on renvoie le reste de la trame qui contient une donnée partiel sinon
        if idx_begin !=-1:
            incomplete_end = frame[idx_begin:-1]
        else:
            incomplete_end = None

        return(incomplete_beginning,incomplete_end,messages)


def select_msg_type(list,type):
    # Rnvoie seulement les messages de la liste arg=list dont le type est arg=type
    list_of_type = []
    for msg in list:
        if msg[:5]==type:
            list_of_type.append(msg)
    return list_of_type

"""---------------------------------Connection to router and socket-----------------------------------------"""
# Connection au réseau WIFI en spécifiant le SSID et le mot de passe
wlan = network.WLAN(mode=network.WLAN.STA)

wlan.connect('SSID', auth=(network.WLAN.WPA2, 'password'))

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


"""--------------------------------GPS instruction loop-----------------------------------------"""
# Initialiser la lecture du de données I2C
i2c = machine.I2C(0, mode=I2C.MASTER, pins=('P22', 'P21'))
scan = i2c.scan()
addr = scan[1]

# Initialisation des données reçues
msg_list = []
prev_incomplete_end = None
MSG_TYPE = 'GPGGA'

while True:
    # Decodage de la trame reçue
    current_frame = read_byte(addr)

    # Lecture et identification des messages de la trame
    incomplete_beg, incomplete_end, complete_msgs = read_msg(current_frame)

    # Reconstruction des messages troncqués
    if prev_incomplete_end != None:
        msg_list.append(prev_incomplete_end+incomplete_beg)

    # Ajout des messages complets à la liste des messages
    for message in complete_msgs:
        msg_list.append(message)

    # Emplacement du message tronqué
    prev_incomplete_end = incomplete_end

    # Extraction du type de données voulues
    msg_list = select_msg_type(msg_list,MSG_TYPE)

    if len(msg_list) > 0:                   # Teste si la liste comprend au moins 1 message
        new_msg = msg_list.pop().split(',') # Lecture des message

        # Teste si le message contient au moins une latitude et une longitude
        if len(new_msg)>5:
            if (new_msg[2] == '' or new_msg[3] == '' or new_msg[4] == '' or new_msg[5] == ''):  # Teste si la donnée est valide
                print('No GPS data available')

            else:
                # Si les données sont valides on les transforme au bon order de grandeur pour un affichage correct sur la map
                coords = [str(float(new_msg[2])/100),new_msg[3],str(float(new_msg[4])/100),new_msg[5]]
                print(coords)
                (clientsocket, address) = s.accept()
                # On met la donnée dans la socket, elle est à disposition de celui qui fait une requête sur la socket
                client_connect(clientsocket, coords[0], coords[2])

    time.sleep_ms(500)

s.close()
