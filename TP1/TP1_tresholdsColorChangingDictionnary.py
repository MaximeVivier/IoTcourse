# Maxime VIVIER
# Adrien LAFFARGUE
import pycom as pc
import time
import machine

# Initialiser la lecture du pin analogique
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13',attn=machine.ADC.ATTN_11DB)   # create an analog pin on P16
pc.heartbeat(False)

# Définition du dictionnaire de couleurs en fontions du palier
colors = {
   0: 0x835eff,
   1: 0x1d4fff,
   2: 0x6de8fa,
   3: 0x73daa6,
   4: 0xb8cf64,
   5: 0xfce24c,
   6: 0xef873e,
   7: 0xf54e31,
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
    k = 512

    # Calcul du quotient de la valeur du capteur divisé par
    # la taille de l'intervalle pour trouver dans quel interval
    # le potar se situe
    q = val//512

    # On trouve la couleur grâce au dictionnaire précédemment créé
    new_color = colors[q]

    # De même on change la couleur de la LED uniquement si le potar
    # change d'intervalle
    if new_color != current_color:
        changeColor(q)
        current_color = new_color
    
    # Répeter cette opération tous les dixièmes de seconde
    time.sleep(0.1)
