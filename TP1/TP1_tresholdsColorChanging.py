# Maxime VIVIER
# Adrien LAFFARGUE
import pycom as pc
import time
import machine

# Initialiser la lecture du pin analogique
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16
pc.heartbeat(False)

# Définition du dictionnaire de couleurs en fontion de leur nom
colors = {
    'magenta' : 0x835eff,
    'bleu' : 0x1d4fff,
    'cyan' : 0x6de8fa,
    'vert_do' : 0x73daa6,
    'vert' : 0xb8cf64,
    'jaune' : 0xfce24c,
    'orange' : 0xef873e,
    'rouge' : 0xf54e31,
}

# Fonction à appeler pour changer la couleur de la LED
def changeColor(color):
    hexa = colors[color]
    pc.rgbled(hexa)
    return()

current_color = ''

while True:
    # Lecture de la valeur du PIN
    val = apin()

    # Définition de la taille des intervalles sachant qu'on en veut 8
    k = 512

    # Initialiser la valeur de nouvelle couleur à trouver en focntion
    # de la position du potar.
    new_color = ''

    # Disjonction des cas en fonction de la position du potar
    # affectation à la variable new_color
    if val<k:
        new_color = 'magenta'
    elif val>1*k and val<2*k:
        new_color = 'bleu'
    elif val>2*k and val<3*k:
        new_color = 'cyan'
    elif val>3*k and val<4*k:
        new_color = 'vert_do'
    elif val>4*k and val<5*k:
        new_color = 'vert'
    elif val>5*k and val<6*k:
        new_color = 'jaune'
    elif val>6*k and val<7*k:
        new_color = 'orange'
    elif val>7*k:
        new_color = 'rouge'

    # Si la nouvelle couleur est la même que l'actuelle
    # on ne fait rien, la LED garde la même couleur
    if new_color != current_color:
        changeColor(new_color)
        current_color = new_color
    
    # Répeter cette opération tous les dixièmes de seconde
    time.sleep(0.1)
