import machine
from machine import I2C
import pycom
import sys
import time
import network
import usocket

def client_connect(clientsocket, latitude, longitude):

    r = clientsocket.recv(4096)
    if len(r) == 0:
        clientsocket.close()
        return
    else:
        print("Received: {}".format(str(r))) #uncomment this line to view the HTTP request

    http = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n"
    mapGPS =  '<html><head><meta charset="utf-8"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.1/dist/leaflet.css" integrity="sha512-Rksm5RenBEKSKFjgI3a41vrjkw4EVPlJ3+OiI65vTjIdo9brlAacEuKOiQ5OFh7cOI1bkDwLqdLw3Zg0cRJAAQ==" crossorigin="" /><style type="text/css">#map{height:400px;}</style><title>Carte</title></head><body><div id="map"></div><script src="https://unpkg.com/leaflet@1.3.1/dist/leaflet.js" integrity="sha512-/Nsx9X4HebavoBvEBuyp3I7od5tA0UzAxs+j83KgC8PU0kgB4XiK4Lfe4y4cgBtaRJQEIFCW+oC506aPT2L1zw==" crossorigin=""></script><script type="text/javascript">var lat =' + str(latitude) + ';var lon =' +str(longitude)+';var macarte = null;function initMap() {macarte = L.map(\'map\').setView([lat, lon], 11);L.tileLayer(\'https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png\', {attribution: \'données © <a href="//osm.org/copyright">OpenStreetMap</a>/ODbL - rendu <a href="//openstreetmap.fr">OSM France</a>\',minZoom: 1,maxZoom: 20}).addTo(macarte);var marker = L.marker([lat, lon]).addTo(macarte);}window.onload = function(){initMap(); };</script></body></html>'
    
    if "GET / " in str(r):
        clientsocket.send(http + mapGPS)
    clientsocket.close()

# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)

#### MPD EFFACER -----------------------------------------------------------------------------------------
wlan.connect('ssid', auth=(network.WLAN.WPA2, 'secret'))
#### MPD EFFACER -----------------------------------------------------------------------------------------

while not wlan.isconnected():
    time.sleep_ms(500)
    print("Wifi .. Connecting")
print("Wifi Connected", wlan.ifconfig())

s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
print("s", s)

s.bind((wlan.ifconfig()[0], 8080))

s.listen(1)

while True:
    # Accept the connection of the clients
    (clientsocket, address) = s.accept()
    client_connect(clientsocket, 43.311786, 5.4)
    # Start a new thread to handle the client

    time.sleep(1)
s.close()

i2c = machine.I2C(0, mode=I2C.MASTER, pins=('P22', 'P21'))
scan = i2c.scan()

while True:
  trame = i2c.readfrom(scan[1],255)
  print(trame)
  print(trame.decode().replace('\n',''))
  print('\n')
  time.sleep_ms(500)