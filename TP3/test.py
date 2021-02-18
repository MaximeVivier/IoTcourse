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

"""---------------------------------Connection to router-------------------------------------------------"""
# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)

#### MPD EFFACER -----------------------------------------------------------------------------------------
wlan.connect('Freebox-5FB8C7', auth=(network.WLAN.WPA2, 'hispanarum#&-orthodoxi*-ructent-eusebio*'))
#wlan.connect('ssid', auth=(network.WLAN.WPA2, 'password'))
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

"""-------------------------------------GPS functions-------------------------------------------------"""

def read_byte(add):
    return i2c.readfrom(add,255).decode()

def read_msg(frame):
    messages = []
    idx_end_of_incomplete_beginning = frame.find('\r\n')
    if idx_end_of_incomplete_beginning == -1:
        #print('Empty')
        return()
    else:
        #print('Not empty')
        incomplete_beginning = frame[:idx_end_of_incomplete_beginning]  #incomplete message at the beginning of the frame
        frame = frame[idx_end_of_incomplete_beginning:]

        idx_begin = frame.find('$')
        idx_end = frame.find('\r\n')
        messages_remaining = (idx_begin !=-1 and idx_begin != -1)       #tests if there are complete messages in the frame
        while messages_remaining:
            messages.append(frame[idx_begin+1:idx_end])                 #adds the comlete message to the message list

            frame = frame[idx_end+2:]                                   #get rid of the detected message in the original frame
            idx_begin = frame.find('$')
            idx_end = frame.find('\r\n')
            messages_remaining = (idx_begin !=-1 and idx_begin != -1)   #tests if there will be a new complete msg

        if idx_begin !=-1:
            incomplete_end = frame[idx_begin:-1]
        else:
            incomplete_end = None

        return(incomplete_beginning,incomplete_end,messages)


def select_msg_type(list,type):
    "Returns only the messages of the selected type from the given list of messages"
    list_of_type = []
    for msg in list:
        if msg[:5]==type:
            list_of_type.append(msg)
    return list_of_type

"""--------------------------------GPS instruction loop-----------------------------------------"""

i2c = machine.I2C(0, mode=I2C.MASTER, pins=('P22', 'P21'))
scan = i2c.scan()
addr = scan[1]

msg_list = []
prev_inc_end = None
MSG_TYPE = 'GPGGA'

while True:
    current_frame = read_byte(addr)
    inc_beg, inc_end, complete_msgs = read_msg(current_frame)
    if prev_inc_end != None:
        msg_list.append(prev_inc_end+inc_beg)
    for message in complete_msgs:
        msg_list.append(message)
    prev_inc_end = inc_end

    msg_list = select_msg_type(msg_list,MSG_TYPE)
    if len(msg_list) > 0:                   # checks if list contains at least 1 message
        new_msg = msg_list.pop().split(',') # then reads it
        if len(new_msg)>5:                  # checks if the message contains at least latitude and longitude
            if (new_msg[2] == '' or new_msg[3] == '' or new_msg[4] == '' or new_msg[5] == ''):  # checks if data is valid
                print('No GPS data availale')
            else:
                coords = [new_msg[2],new_msg[3],new_msg[4],new_msg[5]]
                print(coords)

    time.sleep_ms(500)
