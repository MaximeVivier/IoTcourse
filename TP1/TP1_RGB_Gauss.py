import pycom as pc
import time
import machine
import math


I = 100 # Intensité de la LED de 0 à 255
mu_R = 100 # Position du rouge vert et bleu de 0 à 100
mu_G = 50
mu_B = 0
sigma = 30 # largeur de la gaussienne de chaque couleur

# Définition de la fonction gaussienne
def gauss(x,mu,sigma,i):
    p = math.exp(-(x-mu)**2/(2*sigma**2))
    return round(i*p)

# Initialiser la lecture du pin analogique
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P13

# Désactiver le clignotment de la LED du au fonctionnement classique de la pycom
pc.heartbeat(False)

while True:
    # On lit la valeur du pin.
    val = apin()

    # On transpose la valeur du potar dans l'échelle de 0 à 100 posée au départ
    x = round(val*100/4096)

    # Calcul de l'intensité de rouge à mettre dans la LED à partir de sa
    # valeur sur la gaussienne
    red = hex(gauss(x,mu_R,sigma,I))
    #si la valeur est inférieure à 16 on force le codage sur 2 digits
    if len(red)<4:
        red = '0x0' + red[-1]
    
    # De même pour le vert et le bleu
    green = hex(gauss(x,mu_G,sigma,I))
    if len(green)<4:
        green = '0x0' + green[-1]
    
    blue = hex(gauss(x,mu_B,sigma,I))
    if len(blue)<4:
        blue = '0x0' + blue[-1]
    
    hexa = '0x'+ red[2:] + green[2:] + blue[2:]

    # Changement de la couleur de la LED
    pc.rgbled(int(hexa,16))

    # Répeter cette opération tous les dixièmes de seconde
    time.sleep(0.1)
