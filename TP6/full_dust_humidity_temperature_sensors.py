# Maxime VIVIER
# Adrien LAFFARGUE
import machine, pycom, sys, time, network, usocket
import pycom as pc
from machine import I2C

pc.heartbeat(False)

# ------------------------------------ Définition des constantes pour les acquisitions ------------------------------------------
resolution_temp = 0.0625 #augmentation de tempé pour une incrémentation dans le codage

# Matric des seiuls pour la mesure de l'humidité en fonction des températures
HR = [  [0.76,0.73,0.70,0.67,0.63,0.60,0.56],
        [1.06,1.03,1.03,1.02,0.99,0.96,0.93],
        [1.36,1.34,1.35,1.36,1.34,1.32,1.29],
        [1.67,1.66,1.67,1.68,1.67,1.66,1.64],
        [1.97,1.97,1.98,1.98,1.98,1.98,1.96],
        [2.25,2.25,2.26,2.26,2.26,2.26,2.25],
        [2.51,2.51,2.50,2.51,2.50,2.50,2.48],
        [2.73,2.72,2.70,2.73,2.70,2.68,2.66]    ]

temp_list = [10,15,20,25,30,35,40]
HR_list = [20,30,40,50,60,70,80,90]


# facteur beta dans la formule de calcul de densité de particule
alpha = 0.6

# Constante pour la focntion affine dans la formule de calcul de densité de particule
V0 = 0.41
threshold_dust_sensor_saturation = 3.6 # Volts
# ------------------------------------------------------------------------------------------------------------------------------


#-------------------------------------------- Initialisation des pins d'acquisition--------------------------------------------
# Lecture du capteur de température qui fonctionne avec le protocole I2C
i2c = I2C(0, pins=('P9','P10'))
i2c.init(I2C.MASTER, baudrate=20000)
adresse_temp_sensor = i2c.scan()[0] # contient l'adresse du capteur

# Initialiser l'output pour trigger les mesures du capteur de particules
output_dust_light = machine.Pin('P21', mode=machine.Pin.OUT)

# Initialiser la lecture du pin analogique
adc = machine.ADC()             # create an ADC object
get_humidity_input = adc.channel(pin='P18',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16
get_dust_input = adc.channel(pin='P20',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16
# ------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------------
# Utile pour dans la fonction measure humidity l.95
def compute_ratio(threshold1, threshold2, actual_value):
  return((actual_value - threshold1)/(threshold2 - threshold1))

def measure_temperature():
  [MSB,LSB] = i2c.readfrom(adresse_temp_sensor,2) # On lit la derniere valeur dans le registre du capteur
  output_hex = hex(MSB) + hex(LSB)[2] # on se débarasse des 4 derniers bits du LSB
  output_dec = int(output_hex)
  temperature = output_dec * resolution_temp
  return(temperature)

def measure_humidity(temperature):

  volt_RH_sensor = get_humidity_input()*3.3/4096 # tension de sortie du capteur d'humidité

  # print('Voltage ', volt_RH_sensor)

  index_HR, volt_diff_min = 0, 10000

  round_temp = (temperature // 5)*5 + 5*round((temperature%5)/5)

  col_temp = temp_list.index(round_temp)
  # print(col_temp)
  # print(HR[0][col_temp])

  if volt_RH_sensor < HR[0][col_temp]:
    # En dessous du seuil d'humidité msurable on renvoie 20% avec un message
    # print('En dessous du seuil d\'humidité mesurable')
    HR_final = HR_list[0]
  elif volt_RH_sensor > HR[-1][col_temp]:
    # Au dessus du seuil d'humidité msurable on renvoie 90% avec un message
    # print('Au dessus du seuil d\'humidité mesurable')
    HR_final = HR_list[-1]
  else:
    # Toujours à température mesurée, on repère ici l'index de la ligne pour lequel la
    # tension du potar (donc du capteur d'humidité) est compris entre les valeurs de
    # tension à index_HR et index_HR + 1.
    for lgn_HR in range(len(HR_list)-1):
      diff1 = HR[lgn_HR][col_temp] - volt_RH_sensor
      diff2 = HR[lgn_HR+1][col_temp] - volt_RH_sensor
      if diff1*diff2 < 0:
        index_HR = lgn_HR
        break
    
    # On récupère de la boucle précédante les deux tensions qui entourent l'output du potar.
    # On calcul ici la position de la valeur de tension dans l'intervalle déterminé.
    # On obtient un ratio.
    ratio = compute_ratio(HR[lgn_HR][col_temp], HR[lgn_HR+1][col_temp], volt_RH_sensor)

    # On applique le ratio aux valeurs rondes d'humidité pour en retirer une valeur interpolée
    # Nous avons décidé de faire une interpolation pour l'humidité car les écarts de tension
    # entre deux valeurs étaient élevés. Nous avons décidé seulement d'arrondir à la température
    # la plus proche car les écarts de valeur de tension entre 2 temprératures voisines peuvent
    # être négligeables.
    HR_final = HR_list[index_HR] + 10*ratio
  return(HR_final)

# facteur beta dans la formule de calcul de densité de particule
def beta(humidity):
  if humidity <= 50:
    return(1)
  else:
    return((1-0.01467(humidity-50)))

# Entrée du dust sensor à 0 quand on veut réaliser une mesure et entrée à 1 quand on arrête le créneau
def light_state(state: str):
  if state == 'ON':
    #print('ON')
    output_dust_light.value(0)
  elif state == 'OFF':
    #print('OFF')
    output_dust_light.value(1)

# Calcul de la valeur exacte de la densité de particules enfonction de l'humidité et de la valeur mesurée sur la capteur
def measure_dust(humidity, dust_input):
  tension = dust_input*5/4096
  if tension < threshold_dust_sensor_saturation:
    return(alpha*beta(humidity)*(tension-V0))
  else:
    return(alpha*beta(humidity)*(threshold_dust_sensor_saturation-V0))

# Réaliser l'enchainement de switch ON switch OFF selon les timings de la documentation
def send_pulse_and_measure_dust():
  temperature = measure_temperature()
  # temperature = 25
  humidity = measure_humidity(temperature)
  # humidity = 40
  light_state('ON')
  time.sleep_us(280)
  dust = get_dust_input()
  time.sleep_us(40)
  light_state('OFF')
  time.sleep_us(10000-320)
  return(dust, humidity)
# ------------------------------------------------------------------------------------------------------------------------------

# ------------------------------- Serveur ------------------------------------------------------------------------
# Désactiver le clignotment de la LED du au fonctionnement classique de la pycom
pc.heartbeat(False)

# Initialiser la lecture du de données I2C
adc = machine.ADC()
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)


def client_connect(clientsocket, dust):
    r = clientsocket.recv(4096)
    if len(r) == 0:
        clientsocket.close()
        return
    else:
        # Quand une requête est reçue on l'affiche
        print("Received: {}".format(str(r)))
    
    # On mesure la tension renvoyée par le potar
    # On créé les headers et le body de la réponse qui est simplement une page HTML avec la map
    # Le body HTML contient la donnée de tension mesurée précédemment
    http = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection:close \r\n\r\n"
    mapGPS =  '<!DOCTYPE html><html manifest="site.manifest"><head><meta charset="utf-8"><title>Serveur web</title></head><style>body {hight: 100%;} div {display: flex;flex-direction: column;align-items: center;}</style><body><div id="main"><h1>Lopy server</h1><p>Dust density ' + str(dust) + ' mg/m3</p></div></body></html>'
    # Si la requête faite est une méthode GET, on renvoie la concaténation des headers et du body
    if "GET / " in str(r):
        clientsocket.send(http + mapGPS)
    
    # Une fois les données renvoyées on ferme la socket
    clientsocket.close()


# Connection au réseau WIFI en spécifiant le SSID et le mot de passe
wlan = network.WLAN(mode=network.WLAN.STA)

wlan.connect('HUAWEI Y5 2019', auth=(network.WLAN.WPA2, 'robotegab'))

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

# -----------------------------------------------------------------------------------------------------------------------

while True:
  # On écoute si une requête est reçue
  (clientsocket, address) = s.accept()

  list_pour_moy = []
  humidity = 0

  # Dès qu'une requête est reçue on fait l'acquisition de 50 valeurs de 12bits densité de particules
  # qu'on va ensuite moyenner.
  while len(list_pour_moy)<50:
    value_dust, humidity = send_pulse_and_measure_dust()
    list_pour_moy.append(value_dust)

  # Moyenne des valeurs de densité de particules (valeurs de 12bits)
  mean_dust = (sum(list_pour_moy) / len(list_pour_moy))
  
  # Calcul de la valeur de densité de particule en mg/m3
  compute_dust = measure_dust(humidity, mean_dust)

  # Envoie de la donnée en réponse à la requête faite
  client_connect(clientsocket, compute_dust)
  
s.close()